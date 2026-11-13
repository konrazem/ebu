# EBU economic cells
## A study book about balance, exchange, division, growth, and the reasons to act

Study edition completed for the morning handoff on 10 November 2026, with owner-requested source-connection, calibration, and EBU Kirchhoff-like law extensions added later that day. A connected explanation of the ideal quadratic-cell model, with proofs, worked examples, and clearly stated limits. This edition has been reviewed by its author; it has not received an independent mathematical audit.

## Before we begin

Imagine a collection of places where resources are available. We call each one an **economic cell**. An actor can add resource to a cell, withdraw resource from it, or move resource between cells. Existing EBU can also pass between people without any resource movement at that moment.

The central idea is simple:

> An action that reduces the represented imbalance produces a positive EBU contribution. An action that increases it produces a negative EBU contribution.

Our job is to understand the consequences of that rule. Does it encourage useful redistribution? Does a small cell behave differently from a large one? Can someone earn EBU by splitting a cell and joining it again? Can the arrangement of allowed exchanges matter? Does any of this resemble a known physical law?

We will answer these questions in a connected order. We will not introduce a new kind of cell every few pages.

First we meet A. We learn exactly what its amount, reference, and field mean. Then we compare A with a larger version of itself. Then B appears. Only after understanding A and B will we divide cells, join them, and discuss millions of cells.

The mathematical starting point is the quadratic field we have chosen to study:

\[
\Phi_i(x_i)=\frac12K_i(x_i-x_i^*)^2.
\]

This book derives consequences of that choice. It does not claim that conservation alone uniquely selects this equation, or that a field equation has already determined the correct reference for every real resource. These are separate questions. The useful result here is a family of exact, checkable relationships once the cell and its reference are specified.

We use one compatible resource throughout the main examples. Its represented amount is measured in joules. Moving 10 J from A to B means removing the represented 10 J from A and adding those same 10 J to B. We do not assume that any two materials are interchangeable merely because both can be assigned an energy content.

No construction fee, delivery fee, or delay penalty will be invented. If a quantity is absent from the model, we will say what that prevents us from concluding.

### What an economic cell actually is

An economic cell is a defined unit of resource provision together with a rule for valuing changes in its condition. It represents an actual resource amount, a preferred condition, and the response to moving away from or toward that condition. It is more than a container: a container tells us what it holds, while a cell also tells us what a specified change means in EBU.

The cell does not have to be the source that originally supplied the resource. A source can deliver resource, stop delivering, or disappear while the cell continues to exist. A later withdrawal changes the cell. It does not automatically change the distant source or require the cell to copy the source's current condition.

The cell's field is its present imbalance value, not an additional pile of resource. A cell can contain resource while its field is zero, because it is exactly at its reference. Equally, two cells with the same resource amount can have different field values if their references or responses differ.

### How we specify a cell before using it

To design an ideal cell in this study, we must give the following information. This is a mathematical design, not a design for the machinery or measuring equipment.

| Part of the design | What must be stated |
|---|---|
| Resource and amount \(x\) | What resource is represented, what belongs to the cell, and how its quantity is expressed in joules |
| Reference \(x^*\) | The preferred amount represented by zero imbalance |
| Response \(K>0\) | How strongly the field grows as the amount departs from the reference; its unit is inverse joules |
| Permitted conditions | Which amounts are physically allowed; the field does not itself create a tank's limits |
| Permitted changes | What additions, withdrawals, and transfers actors can actually make, with each actual change identified once |
| EBU rule | How the current field contributions become one signed account update for the completed action |

Once these are specified, we use the same field throughout:

\[
\boxed{\Phi(x)=\frac12K(x-x^*)^2.}
\]

In a first ideal example we may explicitly assume a reference and a response. Applying it to a real resource then requires a reason for those parameter values and a valid resource-to-joule conversion. Naming a preferred condition does not establish that it guarantees long-run survival. Chapters 38–39 explain the physical connection and possible ways to determine K without changing this equation.

K is the cell's response, not its EBU balance. At the same departure from the reference, twice K means twice the field and twice the field slope. Within one fixed cell it is constant during the actions studied here. Under proportional division, the resulting cells inherit transformed K values according to the split rule; they do not receive arbitrary new responses. This is why cell size, reference, and K must be specified together.

### How the cell produces and consumes EBU

When we say that a cell produces EBU, we mean that an identified action reducing its field has a positive signed contribution. When we say it consumes EBU, we mean that an identified action increasing its field has a negative signed contribution. A payment of existing tokens to another participant is different: that payment transfers units rather than creating or consuming them.

For one actor performing the complete identified change of one otherwise unchanged cell, the signed amount is

\[
\boxed{E=\frac{\Phi_{\rm before}-\Phi_{\rm after}}{W_{\mathrm{Cs}}}.}
\]

E is measured in EBU units. The fixed ruler is

\[
W_{\mathrm{Cs}}=h\nu_{\mathrm{Cs}}
=6.091102297113866550\times10^{-24}\ {\rm J},
\]

where h is Planck's constant and \(\nu_{\mathrm{Cs}}=9\,192\,631\,770\ {\rm Hz}\) is the fixed cesium reference frequency. We use the same ruler for all these cells.

Take the cell introduced in Chapter 1: its reference is 100 J and K is 1/(100 J). At 20 J of resource its field is 32 J. Adding 40 J brings the amount to 60 J and reduces the field to 8 J. The field reduction is 24 J, so this identified action produces 24/W_Cs EBU units. The 40 J delivered and the 24 J field reduction are different quantities. We reward the reduction in represented imbalance, not simply every joule delivered at a fixed one-for-one rate.

Reversing that exact change, from 60 J back to 20 J, raises the field by 24 J and consumes the same EBU amount. The round trip creates zero net EBU. At the reference, moving away in either permitted direction increases the field. Above the reference, removing resource can improve the condition instead of worsening it. The sign follows the actual change in imbalance, not merely the labels “supply” and “withdrawal.”

During an action the field reflects the changing resource amount. The actor can adjust what remains to be done. This book uses the working ideal in which the exact completed account amount is applied once after the action; it does not freeze the initial slope or issue a second reward at completion. For parallel contributions we use their individually identified current changes, not a copy of the whole endpoint difference for each actor.

### The atom analogy: a change of state and a matching exchanged amount

In the ideal radiative-transition description, an atom moving from an upper energy level to a lower one emits a photon with energy equal to the level difference. Absorption can take it in the opposite direction. The relation is

\[
E_{\rm upper}-E_{\rm lower}=h\nu.
\]

Here ν is the photon frequency. This is the energy-level relation used in [NIST's introduction to atomic spectroscopy](https://physics.nist.gov/Pubs/AtSpec/node01.html). It supplies a precise comparison for the cell's state change:

| Atomic transition | Economic-cell contribution |
|---|---|
| Atomic energy decreases and radiation carries the released energy | Cell field decreases and the matching positive EBU contribution is created |
| Absorbed radiation raises atomic energy | An action raises the cell field and the matching EBU contribution is negative |
| The exchanged photon energy follows the energy-level difference | The EBU amount follows the complete field difference through the fixed ruler |

This is why the analogy is useful: the exchanged amount is tied to a change of state. It is not an arbitrary reward for naming an action. In our model the corresponding complete balance is \(W_{\mathrm{Cs}}G+\sum_i\Phi_i=\text{constant}\), when all relevant field changes and matching account contributions are included once. G means the total existing EBU in the modeled accounts.

For a positive field reduction, define its energy-equivalent frequency by

\[
\nu_{\rm change}=\frac{\Phi_{\rm before}-\Phi_{\rm after}}h.
\]

Then the positive EBU amount can equally be written

\[
\boxed{
E=\frac{h\nu_{\rm change}}{h\nu_{\mathrm{Cs}}}
=\frac{\nu_{\rm change}}{\nu_{\mathrm{Cs}}}.
}
\]

h cancels in this ratio. For an increase in field, the same calculation with the positive magnitude gives the amount consumed, while the signed contribution is negative. This changes the units in which we express the same result; it does not change the field.

The analogy concerns energy differences and conservation. An atom has quantum states and physical radiation; our present cell model has a continuous resource coordinate and transferable accounting units. It does not derive photon properties, discrete token sizes, or atomic energy levels for economic cells. In particular, one EBU is not being identified with one emitted photon. The useful correspondence is the matching state change, not a literal identity of the objects.

### Why the cell is important to the economy

A cell turns a specified resource change into a current, signed incentive. It tells an actor how much an addition, withdrawal or transfer improves or worsens the represented condition. People can then exchange the resulting EBU with others, without pretending that every payment moves physical resource at that moment.

Independent cells keep their own fields. The economy connects them through actors' choices and transferable EBU, not through an assumed physical wire. Their fields still add for conservation checks, even though a payment to someone near B does not directly change A's field. Later chapters examine when cooperation, redistribution, division and joining allow better outcomes under these same rules.

### Where the Gaussian bell and K enter

Our quadratic field is a bowl: its lowest point is at x*. A Gaussian probability distribution is a bell: its highest point is at its centre. They are not the same curve. There is, however, an important conditional connection.

Suppose the observed condition x has a justified probability density proportional to \(\exp[-\Phi(x)/\Theta]\), where Θ is an independently known positive energy scale in joules and the state measure is appropriate. For the quadratic field on the full real line, this is a Gaussian with variance

\[
\boxed{\sigma^2=\Theta/K,\qquad K=\Theta/\sigma^2.}
\]

The variance σ² measures the squared spread of x around its mean and has units J² here. At the same Θ, a stronger K gives a narrower bell; a weaker K gives a wider bell. A physical example is the equilibrium distribution of a harmonic coordinate, as derived in [MIT's canonical-ensemble lecture](https://live.ocw.mit.edu/courses/8-044-statistical-physics-i-spring-2013/8060bdb2909016322cc323d867682179_MIT8_044S13_L13.pdf).

This is a possible way to determine K, not a replacement field or a universal assumption about economic observations. It requires the right observed coordinate, a justified statistical relation, and an independently established energy scale. A bell-shaped source-output history alone supplies none of those guarantees. Bounded resource amounts also require appropriate boundary treatment rather than blindly using a full Gaussian. Chapter 39 develops these points and the checks needed after division.

The three pictures therefore have different jobs: the quadratic field defines the value of imbalance; the atom comparison explains matching state changes and exchanged amounts; the Gaussian connection can, under its own premises, help infer the response K. None replaces the others.

### How to read the equations

An equation is not meant to replace the explanation. Each important equation will be followed by its meaning in ordinary language.

There are three particularly important quantities:

- \(x\): how much represented resource the cell currently contains;
- \(x^*\): the amount at which this cell's represented imbalance is zero;
- \(\Phi\): the size of its imbalance, expressed in joules.

The star in \(x^*\) is part of the name. It does not mean multiplication.

We will also use \(m\), the **current slope**. Read it as: “How much does the field change per next small joule added here?” This is the quantity that connects the shape of the field to an actual decision. It is not the cell's resource amount and it is not its EBU balance.

The same cell can contain a positive amount of resource and have zero imbalance. Conversely, two cells can contain the same resource amount and have different imbalances because their reference amounts differ.

The examples use modest numbers of joules so that the arithmetic is readable. The corresponding number of EBU is very large because the cesium energy reference is very small. We will often calculate the joule-valued numerator first and write “divide by \(W_{\mathrm{Cs}}\)” afterward.

Some chapters compare alternative operations from a stated starting condition. Such a comparison is not a free physical reset: returning a real cell to that starting condition would have its own signed contribution. We keep the same family of cells throughout, but distinguish a new comparison from the next action in an actual sequence.

### A small dictionary for the changes

You do need to learn the symbols, but you do not need to learn them all at once. These five are enough to begin:

| Expression | Read it aloud as | Concrete meaning |
|---|---|---|
| \(\Delta x\) | “change in the amount” | Final amount minus starting amount; for example, \(40-20=20\) J |
| \(dx\) | “an infinitesimal change in the amount” | The ideal limit of a smaller and smaller step |
| \(d\Phi/dx\) | “field change per change in amount” | The slope at the cell's present condition |
| \(\int m\,dx\) | “add the slope times each little change” | The complete field change along the actual operation |
| \(\sum_i\Phi_i\) | “add the fields of all these cells” | A total for the collection, not a new connection between cells |

The small letter \(d\) is not a multiplier and does not mean time. A change of amount can be described without specifying how many seconds it takes. We will use the capital \(\Delta\) for a whole finite difference and the small \(d\) for the differential rule.

There is also an important difference between **resource movement** and **EBU payment**. Adding resource changes a cell's \(x\) and can produce an EBU contribution. Paying someone with EBU that already exists changes who holds those tokens. The payment, by itself, does not change a cell's \(x\). Later chapters will connect these two activities without treating them as the same event.

### Reading map

| Part | Question it answers | Chapters |
|---|---|---|
| I | What is a cell, and how does an actual change earn or consume EBU? | 1–4 |
| II | What changes when A is larger, B is smaller, or they exchange resource? | 5–8 |
| III | What is the difference between total shortage and unequal distribution? | 9–11 |
| IV | How do division and joining preserve the laws? | 12–15 |
| V | How do participants cooperate, and what is conserved? | 16–19 |
| VI | What do lines, rings, groups, and routes change? | 20–25 |
| VII | When does choosing the best current action give a least-resource path? | 26–28 |
| VIII | What happens under repeated division, growth, and recursive patterns? | 29–34 |
| IX | Which incentives and physical connections have actually been established? | 35–37 |
| X | How does a source supply this same cell, and when can observations identify K? | 38–39 |
| XI | What are the EBU counterparts of Kirchhoff's laws, and what do they require? | 40 |

If you are tired, read Chapters 1–3 first. Then read Chapters 6–8. The many-cell formula in Chapter 9 will be much easier once the 40 J transfer between A and B is familiar.

---

# Part I. Understanding one cell before connecting the economy

## 1. Meet cell A

Let A have the following properties:

\[
x_A^*=100\ {\rm J},
\qquad
K_A=\frac1{100\ {\rm J}}.
\]

The reference amount is 100 J. The number \(K_A\) tells us how strongly the field changes when A moves away from that reference.

For this cell,

\[
\Phi_A(x_A)=\frac{(x_A-100\ {\rm J})^2}{200\ {\rm J}}.
\]

Suppose A currently contains 20 J. It is 80 J below its reference. Its field value is

\[
\Phi_A(20\ {\rm J})
=\frac{(80\ {\rm J})^2}{200\ {\rm J}}
=32\ {\rm J}.
\]

Now compare four conditions:

| Resource in A | Difference from its reference | Field value |
|---|---:|---:|
| 20 J | 80 J below | 32 J |
| 60 J | 40 J below | 8 J |
| 100 J | Exactly at the reference | 0 J |
| 140 J | 40 J above | 8 J |

Notice the last row. In this model, being above the reference can also be an imbalance. The reference is not automatically the maximum amount that the container can physically hold.

That distinction matters. If 100 J were an absolute physical maximum, then the 140 J state would simply be forbidden. If A can hold 140 J but its reference is 100 J, the state is permitted and has a positive field value.

We must decide which physical states exist before applying a formula to them. The quadratic equation does not itself declare every nonnegative amount physically possible.

### Why is there a square?

The square gives the field two properties:

1. Departures on either side of the reference have positive imbalance.
2. Larger departures become progressively more expensive in field value.

For A, doubling a departure from 40 J to 80 J multiplies the field by four, from 8 J to 32 J.

This is not an average. The factor \(1/2\) appears because the slope we want is linear:

\[
\frac{d\Phi_A}{dx_A}=K_A(x_A-x_A^*).
\]

The integral of \(K_A(x_A-x_A^*)\) is \(\tfrac12K_A(x_A-x_A^*)^2\). Choosing zero field at \(x_A=x_A^*\) removes the otherwise arbitrary additive constant.

### What this equation does not tell us

The equation tells us the field once \(x_A\), \(x_A^*\), and \(K_A\) are known.

It does not yet tell us why the right reference for a particular application is 100 J rather than 80 J. It also does not tell us what machinery moves the resource. We are specifying the reference for this study, then checking the mathematical consequences; we are not claiming to have derived that reference from the resource itself.

For now, we study a specified ideal cell. This allows us to derive its consequences precisely. Later we will identify which consequences depend on how its reference is established.

**What we now know:** the amount of resource and the amount of imbalance are different quantities. Next we connect a change in imbalance to EBU.

## 2. What earns EBU, and what consumes it?

Our fixed reference energy is

\[
W_{\mathrm{Cs}}=h\nu_{\mathrm{Cs}}
=6.091102297113866550\times10^{-24}\ {\rm J}.
\]

It is the energy ruler. It does not change when a cell becomes depleted, when another cell appears, or when people transfer EBU.

Begin with the value of a change happening now. At A's current amount, define

\[
m_A=K_A(x_A-x_A^*).
\]

An identified differential addition \(dx_A\) has contribution

\[
dE_A=-\frac{m_A\,dx_A}{W_{\mathrm{Cs}}}.
\]

At A's starting amount of 20 J, its slope is \(-0.8\). An addition therefore lowers the field and gives a positive contribution. As the amount changes, the slope changes too. The complete value adds these current contributions; it does not keep using \(-0.8\) for the whole operation.

For a complete identified change of A, with its reference and \(K_A\) unchanged, the signed contribution is

\[
E_A=
\frac{\Phi_A(\text{before})-\Phi_A(\text{after})}
{W_{\mathrm{Cs}}}.
\]

A positive result means that the contribution produces EBU. A negative result means that it consumes EBU. The word “signed” simply means that we retain the plus or minus sign.

Start at 20 J and add 20 J:

\[
E_A(20\rightarrow40)
=\frac{32-18}{W_{\mathrm{Cs}}}\ {\rm J}
=\frac{14\ {\rm J}}{W_{\mathrm{Cs}}}.
\]

Add another 20 J:

\[
E_A(40\rightarrow60)
=\frac{18-8}{W_{\mathrm{Cs}}}\ {\rm J}
=\frac{10\ {\rm J}}{W_{\mathrm{Cs}}}.
\]

The same resource amount earns less on the second addition. Why? Because A is already closer to its reference.

Adding the final 40 J from 60 J to 100 J earns

\[
E_A(60\rightarrow100)
=\frac{8\ {\rm J}}{W_{\mathrm{Cs}}}.
\]

All three additions together earn

\[
\frac{14+10+8}{W_{\mathrm{Cs}}}\ {\rm J}
=\frac{32\ {\rm J}}{W_{\mathrm{Cs}}}.
\]

This is exactly the original field value. We did not earn a different total by dividing the restoration into three actions.

### The value of the next small addition

Define the current slope:

\[
m_A=K_A(x_A-x_A^*).
\]

The symbol \(m_A\) is dimensionless because \(K_A\) has units \(1/{\rm J}\) and the difference has units J.

For an identified small change \(dx_A\),

\[
dE_A=-\frac{m_A\,dx_A}{W_{\mathrm{Cs}}}.
\]

At 20 J, \(m_A=-0.8\). A small positive addition therefore earns approximately \(0.8\,dx_A/W_{\mathrm{Cs}}\).

At 60 J, \(m_A=-0.4\). The same small addition earns approximately half as much.

At 140 J, \(m_A=+0.4\). Adding more consumes EBU. Removing a small amount produces EBU, because removal moves A back toward 100 J.

The word “approximately” applies when we multiply a finite small amount by one slope. The differential formula itself is exact in the limit. For a finite action, we account for the slope changing along the action:

\[
E_A=-\frac1{W_{\mathrm{Cs}}}
\int_{x_{\rm before}}^{x_{\rm after}}
K_A(x_A-x_A^*)\,dx_A.
\]

The integral means: add the values of all the small actual changes. It does not require the actor to know the future field before acting.

### See the finite-change correction directly

Let \(\delta\) mean a finite amount added to A. A negative \(\delta\) means a withdrawal. Let \(x\) be A's starting amount and \(m=K_A(x-x_A^*)\) its starting slope. Expanding the square gives

\[
\begin{aligned}
\Phi_A(x+\delta)-\Phi_A(x)
&=\frac{K_A}{2}
\left[(x+\delta-x_A^*)^2-(x-x_A^*)^2\right]\\
&=m\,\delta+\frac12K_A\delta^2.
\end{aligned}
\]

The first term uses the starting slope. The second term is the exact correction for how the slope changes during this finite addition. Both terms are measured in joules.

For A's addition from 20 J to 40 J,

\[
\Delta\Phi_A
=(-0.8)(20\ {\rm J})
+\frac12\frac1{100\ {\rm J}}(20\ {\rm J})^2
=-16\ {\rm J}+2\ {\rm J}
=-14\ {\rm J}.
\]

So the actual contribution is \(14\ {\rm J}/W_{\mathrm{Cs}}\), not the \(16\ {\rm J}/W_{\mathrm{Cs}}\) obtained by multiplying the entire addition by the initial slope.

Now divide that same addition into two 10 J parts. The first part lowers the field by 7.5 J. The second starts at 30 J, where the slope is \(-0.7\), and lowers it by 6.5 J. Their sum is still 14 J. Smaller decisions change the opportunities to adjust; they do not change the value of the same complete physical change.

This is also a precise definition of the derivative. Divide the field difference by \(\delta\):

\[
\frac{\Phi_A(x+\delta)-\Phi_A(x)}{\delta}
=m+\frac12K_A\delta.
\]

As \(\delta\) becomes smaller and smaller, the last term tends to zero. The ratio approaches \(m\). That is what \(d\Phi_A/dx_A=m_A\) means.

### When does the actor's account change in this book?

We use the owner's working ideal: the actual contribution is evaluated along the physical change, and the exact completed amount changes the actor's account once the action finishes. The field reflects the current physical condition during the action. Waiting to settle the account does not freeze the field at the starting condition.

An actor may adjust the remaining part of an action while seeing these changing conditions. Adjustment does not require advance issuance of the final EBU amount.

For the single-actor examples here, that actor performs the complete identified change. If several actors act together, we add their separate current contributions; we do not give the whole endpoint difference to every actor. Chapters 16–18 explain the accounting and parallel-action cases carefully.

An EBU amount already paid for the same contribution would not be paid again at completion. The book studies the after-action ideal, not an additional payment on top of the older acceptance convention.

### Zero slope does not mean a finite free withdrawal

At 100 J the slope is zero. But withdrawing a finite amount \(q>0\) produces

\[
\Phi_A(100\ {\rm J}-q)=\frac12K_Aq^2.
\]

Its EBU cost is therefore

\[
\frac{K_Aq^2}{2W_{\mathrm{Cs}}}.
\]

The initial slope is zero, but it does not remain zero as the withdrawal proceeds. No finite withdrawal has zero cost merely because it began at the reference.

**First law of this model:** cutting the same actual change into smaller decisions does not change its complete signed value. What changes is that the actor can respond to the current situation along the way.

## 3. Can paying to overfill a cell be an investment?

Yes, it can be a temporary advance of EBU. To understand what is recovered and what is newly earned, we must follow both parts of the operation.

First restore A to its reference of 100 J. Now add 20 J, taking A to 120 J.

Its field rises from zero to

\[
\frac12\frac1{100\ {\rm J}}(20\ {\rm J})^2
=2\ {\rm J}.
\]

The addition therefore costs \(2\ {\rm J}/W_{\mathrm{Cs}}\).

This does not mean that storing resource is always economically foolish. Suppose another cell B needs that resource later.

For this example, let B have

\[
x_B^*=200\ {\rm J},\qquad
K_B=\frac1{200\ {\rm J}},\qquad
x_B=160\ {\rm J}.
\]

B's field is 4 J. Move the extra 20 J from A to B:

- A moves from 120 J to 100 J. Its field falls by 2 J.
- B moves from 160 J to 180 J. Its field falls from 4 J to 1 J, a reduction of 3 J.

The complete transfer produces

\[
\frac{2+3}{W_{\mathrm{Cs}}}\ {\rm J}
=\frac{5\ {\rm J}}{W_{\mathrm{Cs}}}.
\]

But the earlier overfilling cost 2 J on the same ruler. The net result of both actions is

\[
\frac{-2+5}{W_{\mathrm{Cs}}}\ {\rm J}
=\frac{3\ {\rm J}}{W_{\mathrm{Cs}}}.
\]

That is exactly what adding the 20 J directly to B would have produced.

### Where did the five joules of field improvement come from?

Two joules reversed the imbalance we had previously created in A. Three joules repaired B's shortage.

So the later positive amount contains two different things:

1. Recovery of the earlier EBU expense.
2. The positive value of improving B.

Calling all five “new profit” would ignore the earlier expense.

This is the useful sense in which your investment interpretation works. The actor can accept a negative contribution now and later participate in a positive contribution. The later opportunity may justify the earlier decision.

### Does the model charge for waiting?

No. If A stays at 120 J and nothing represented changes, \(\Phi_A\) stays at 2 J. The model does not charge another 2 J every hour or every day.

The negative contribution came from changing A from 100 J to 120 J. It was not a rental fee for the passage of time.

If a real cell leaks, decays, changes its reference, or has some other relevant change, that is a separate physical change to represent. We do not invent such a change merely because time has passed.

### Is recovery guaranteed?

Not as a personal business outcome. The later resource action must actually occur, and the person receiving its contribution must be identified. If one person overfills A and another later performs the useful transfer, the first person's expense does not automatically make the second person's contribution belong to them.

They can agree to transfer existing EBU. That agreement is an economic relationship between them; it does not change the physical attribution.

### General calculation

Let A begin at its reference. Let B be \(d\) below its reference. Put an amount \(p\) into A, then move that same amount into B.

The first contribution is

\[
E_1=-\frac{K_Ap^2}{2W_{\mathrm{Cs}}}.
\]

The second is

\[
E_2=\frac1{W_{\mathrm{Cs}}}
\left[
\frac12K_Ap^2+
K_B\left(dp-\frac12p^2\right)
\right].
\]

Adding them gives

\[
\boxed{
E_1+E_2
=\frac{K_B(dp-p^2/2)}{W_{\mathrm{Cs}}}.
}
\]

The A terms cancel. The final expression is precisely B's field improvement.

For \(0\le p\le d\), every small addition to B is beneficial. If we continue beyond B's reference, some later additions have negative contributions. The complete formula still works for permitted states, but the economic story changes.

### Could division or a changing reference alter the result?

Dividing the overfilled A proportionally does not remove its excess. Every resulting cell has the same ratio above its inherited reference, and their fields still add to A's field. Chapters 12–14 prove this.

A genuine reference change can alter later values, but it is another change in the complete model, not a guaranteed investment return. Chapter 15 shows exactly where that change appears in the equation.

**Second law:** temporary overfilling can be part of a profitable complete operation, but creating an imbalance and later removing that same imbalance does not create a net EBU gain by itself.

## 4. Why the capacitor is a useful physical comparison

An electrical capacitor has charge \(Q\), capacitance \(C_e\), and voltage \(V_e\). Its familiar energy relationships are

\[
V_e=\frac{Q}{C_e},
\qquad
dU=V_e\,dQ,
\qquad
U=\frac{Q^2}{2C_e}.
\]

In words: voltage tells us the work needed for the next small amount of charge. The total stored electrical energy is the integral of that work. These relationships are derived in [Feynman's discussion of capacitor energy](https://www.feynmanlectures.caltech.edu/II_08.html).

Our cell has

\[
m=K(x-x^*),
\qquad
d\Phi=m\,dx,
\qquad
\Phi=\frac12K(x-x^*)^2.
\]

The mathematical roles line up:

| Capacitor | Economic-cell calculation |
|---|---|
| Charge relative to a chosen reference | Resource difference \(x-x^*\) |
| Capacitance \(C_e\) | Reciprocal response \(1/K\) |
| Voltage \(V_e\) | Current field slope \(m\) |
| Electrical energy \(U\) | Imbalance field \(\Phi\) |
| Work for a small charge change | Field change for a small resource change |

This is a comparison of roles, not a claim that joules of resource are electrical charge. The dimensions differ between the columns. Within each column, however, the product of the response and its corresponding change has energy units.

It explains several things we want:

- A larger departure produces a larger response.
- The response is the derivative of the energy-like quantity.
- Two objects can exchange something until their responses agree.
- The total amount can remain unchanged while the distribution and the total energy-like quantity change.

### Where the tokens fit in the comparison

The capacitor comparison identifies an equation and a concrete operation. It does not require us to guess a particle identity for an EBU token.

In our model, tokens express signed field contributions on a fixed energy ruler. Existing tokens can circulate without changing any cell. Capacitor charge, by contrast, is itself part of the capacitor's physical state.

That difference does not destroy the comparison. It tells us exactly which part of physics we are borrowing: the relation between amount, response, and quadratic energy.

### Where does a nonzero reference fit?

For our purposes the capacitor-shaped quantity describes departure from a chosen reference, not necessarily the capacitor's entire physical energy.

If a real apparatus maintains a reference voltage, the apparatus and its energy exchanges matter to a full physical account. We do not get a physically maintained reference for free simply by subtracting \(x^*\).

For the economic cell, choosing and justifying \(x^*\) remains part of specifying what the cell represents. The following results are exact once that specification is fixed.

**What this comparison gives us:** a strong reason to study equal slopes, reciprocal \(K\), and composition laws. We now make A bigger and see what must change.

# Part II. Different sizes and the incentive to redistribute

## 5. Make A twice as large

What should “twice as large” mean?

For two versions of the same type of cell, we use the following meaning:

- the reference amount doubles;
- the current amount doubles;
- the relative condition stays the same.

A cell with 20 J and reference 100 J is at 20% of its reference. A cell with 40 J and reference 200 J is also at 20%.

If we want the next joule to have the same marginal value in these equally supplied cells, we cannot keep \(K\) unchanged.

Originally,

\[
m_A=K_A(x_A-x_A^*).
\]

For the doubled cell, the difference \(x_A-x_A^*\) doubles. To keep \(m_A\) unchanged, \(K_A\) must halve:

\[
x_{\rm large}^*=2x_A^*,
\qquad
x_{\rm large}=2x_A,
\qquad
K_{\rm large}=\frac{K_A}{2}.
\]

More generally, scaling the cell by a positive factor \(a\) gives

\[
x_{\rm large}^*=a x_A^*,\qquad
x_{\rm large}=a x_A,\qquad
K_{\rm large}=\frac{K_A}{a}.
\]

This produces

\[
m_{\rm large}=m_A,
\qquad
\Phi_{\rm large}=a\Phi_A.
\]

The response to the next resource unit stays the same. The total field scales with the amount of cell represented.

### One constant for one cell type

We can write this size rule compactly:

\[
\boxed{K_i x_i^*=\kappa.}
\]

Here \(\kappa\) is the same dimensionless constant for the cell type being studied.

This lets us distinguish two questions that were previously mixed together:

1. Are the cells the same type?
2. Are they the same size?

Same type can mean the same \(\kappa\). It need not mean the same numerical \(K_i\) for every possible size.

If we split one cell into two smaller same-type cells, each smaller cell has a larger \(K_i\). That is not a change of material type; it is the required size dependence.

Define

\[
y_i=\frac{x_i}{x_i^*}.
\]

This is the fraction of the reference amount currently present. Then

\[
m_i=\kappa(y_i-1),
\qquad
\Phi_i=\frac{\kappa x_i^*}{2}(y_i-1)^2.
\]

These two equations will make the rest of the book much easier.

### Is making A bigger an action that earns EBU?

Not from this comparison alone. We have compared two complete cells of different sizes.

Actually creating a larger system introduces resource, reference, and possibly other physical changes. It must not be confused with multiplying the description of an existing cell and claiming the larger field as a newly available reward.

We will handle growth explicitly later. For now we have learned the size law, not a way to obtain a second cell for nothing.

## 6. Add B: a large cell can be less needy than a small one

For the main two-cell comparison, use the original depleted starting condition of A:

\[
x_A^*=100\ {\rm J},\quad x_A=20\ {\rm J},\quad
K_A=\frac1{100\ {\rm J}}.
\]

Now introduce B:

\[
x_B^*=200\ {\rm J},\quad x_B=160\ {\rm J},\quad
K_B=\frac1{200\ {\rm J}}.
\]

Both have \(\kappa=1\).

This is an alternative starting scenario to the investment calculation in Chapter 3. We are not moving the real cells back to these amounts without accounting for it.

A is at 20% of its reference. B is at 80%.

Their slopes are

\[
m_A=-0.8,\qquad m_B=-0.2.
\]

Suppose we can add one small resource amount to either cell. Adding it to A produces more EBU because A's field falls more per added joule.

This is the first concrete redistribution signal:

> For the same type of cell, the next addition is more valuable in the cell that is further below its reference as a fraction of that reference.

It is not simply “give to the smallest cell.” If A contained 90 J while B contained 40 J, A would be at 90% and B at 20%. The larger B would then offer the stronger restoration incentive.

Nor is it “give to the cell containing the fewest joules.” The reference matters. A tiny cell could be full while a much larger one has a large shortage.

### Why can a small cell respond more sharply?

Suppose both cells begin at their references. Remove 10 J from each.

For A:

\[
\Phi_A=\frac{(10\ {\rm J})^2}{200\ {\rm J}}
=0.5\ {\rm J}.
\]

For B:

\[
\Phi_B=\frac{(10\ {\rm J})^2}{400\ {\rm J}}
=0.25\ {\rm J}.
\]

The same withdrawal is 10% of A's reference but only 5% of B's.

This does not prove that small cells are bad. It says that a small cell is more strongly disturbed by the same absolute withdrawal. If the requested amount is proportionally smaller, the comparison changes.

The statement “small cells suit small needs” therefore has a precise limited meaning here: a small absolute withdrawal need not be a small relative withdrawal. The field responds to the latter through the size rule.

**What we now know:** size alone does not determine the best destination. Current amount relative to reference does. Next we remove resource from one cell and add it to the other.

## 7. Move resource from B to A

A is at 20% and B at 80%. Let us move 40 J from B to A.

The before and after conditions are:

| Cell | Before | After | Reference |
|---|---:|---:|---:|
| A | 20 J | 60 J | 100 J |
| B | 160 J | 120 J | 200 J |

Both finish at 60% of their references.

Now calculate each field separately:

- A's field falls from 32 J to 8 J.
- B's field rises from 4 J to 16 J.

The A change produces \(24\ {\rm J}/W_{\mathrm{Cs}}\). The B change consumes \(12\ {\rm J}/W_{\mathrm{Cs}}\).

Together, the operation produces

\[
\boxed{
E_{B\rightarrow A}
=\frac{24-12}{W_{\mathrm{Cs}}}\ {\rm J}
=\frac{12\ {\rm J}}{W_{\mathrm{Cs}}}.
}
\]

No new resource was produced. The total remains 180 J.

That is what “making better use of the resource already present” means in this calculation: the same 180 J is distributed with less disparity relative to the two references.

The phrase does not claim that a joule became more physically energetic. It means the operation improved the particular condition represented by our field.

### Why does the positive contribution not ignore B's loss?

Because B's negative contribution is included.

If we paid the full 24 J-equivalent for A's improvement and forgot B's 12 J-equivalent deterioration, we would violate conservation. The correct total is 12, not 24.

One actor completing the whole identified operation has that complete signed contribution. If different actors perform different parts, the contributions remain separately identified. They can transfer existing EBU between themselves, but the whole 12 must not be awarded to each person.

### Deriving the best transfer amount

To avoid changing the roles of our continuing A and B, call a general donor D and a general receiver R in the following derivation. Let their starting slopes be \(m_D\) and \(m_R\). Transfer \(q\ge0\):

\[
x_D\mapsto x_D-q,\qquad x_R\mapsto x_R+q.
\]

Expanding the two quadratic fields gives

\[
\boxed{
E(q)=
\frac{(m_D-m_R)q-\tfrac12(K_D+K_R)q^2}
{W_{\mathrm{Cs}}}.
}
\]

The first small transfer is beneficial when \(m_D>m_R\).

As the transfer proceeds, the donor's slope falls and the receiver's rises. Their difference becomes

\[
m_D-m_R-(K_D+K_R)q.
\]

The next increment stops producing positive EBU when that difference reaches zero. Therefore

\[
\boxed{
q_{\rm best}=\frac{m_D-m_R}{K_D+K_R}
}
\]

provided \(m_D>m_R\) and this amount is permitted by the cells' physical limits.

If \(m_D\le m_R\), no positive amount in that chosen direction improves the field: doing nothing gives the greatest contribution among \(q\ge0\). The reverse direction may be beneficial if it is allowed. If a physical limit stops a beneficial transfer before \(q_{\rm best}\), the best permitted amount is the amount up to that limit.

For our B-to-A example:

\[
q_{\rm best}
=\frac{-0.2-(-0.8)}{1/200+1/100}\ {\rm J}
=40\ {\rm J}.
\]

When the positive equal-slope amount is permitted, the maximum complete contribution is

\[
\boxed{
E_{\max}=
\frac{(m_D-m_R)^2}
{2W_{\mathrm{Cs}}(K_D+K_R)}.
}
\]

**Redistribution law:** an allowed resource transfer produces positive EBU while it moves resource from the higher slope to the lower slope. The positive incentive ends when those slopes agree, unless a physical limit is reached first.

## 8. Equal responses, not equal resource amounts

After the transfer, A has 60 J and B has 120 J.

Their amounts are not equal. Their slopes are:

\[
m_A=\frac{60-100}{100}=-0.4,
\qquad
m_B=\frac{120-200}{200}=-0.4.
\]

Both cells now assign the same value to the next small addition or withdrawal.

This explains “equal slopes” in concrete terms:

> A further joule has the same current field value at A as at B.

The word “response” refers to that value. It does not mean that the cells contain equal amounts.

### Why can we not keep earning by moving the resource back and forth?

Starting from this equal-slope condition, move an additional amount \(q\) from B to A.

The linear benefit is zero because the starting slopes are equal. The complete contribution is

\[
E(q)=-\frac{(K_A+K_B)q^2}{2W_{\mathrm{Cs}}}.
\]

For any nonzero \(q\), this is negative.

Move 10 J:

\[
E(10\ {\rm J})
=-\frac{0.75\ {\rm J}}{W_{\mathrm{Cs}}}.
\]

The new amounts are 70 J and 110 J, or 70% and 55% of their references. We have created a difference that did not previously exist.

Moving those 10 J back produces \(0.75\ {\rm J}/W_{\mathrm{Cs}}\), exactly reversing the earlier expense. The two-action cycle produces zero net EBU.

### What did equalization repair?

Before redistribution, A was much more depleted relative to its reference than B. After redistribution, both were 40% below their references.

But the combined reference was and remains 300 J. The combined amount was and remains 180 J.

The system is still short by 120 J. Redistribution removed the difference in relative provision; it did not manufacture the missing 120 J.

This is why “equalization removes the difference, not the combined shortage” is important. It separates two problems:

1. There may be too little resource in total.
2. The available resource may also be distributed unevenly relative to the references.

Moving existing resource can solve the second problem without solving the first.

### The capacitor connection

Two connected capacitors reach a common voltage, not necessarily an equal charge. In the elementary equal-capacitance example, the initial energy decreases during charge equalization; that energy must go somewhere physically, such as heat or radiation. [MIT's two-capacitor calculation](https://web.mit.edu/esfaki/www/8.311_files/2.pdf) makes this accounting explicit.

Our exact counterpart is equal field slopes and a decrease of the total quadratic field. That decrease is the numerator of the complete EBU contribution. We are not claiming that the EBU tokens themselves carry the released electrical energy.

**Equalization law:** after all permitted redistribution has brought the slopes to equality, creating a new difference costs EBU. Repairing the same difference can recover that cost, but cannot create a positive closed-cycle total.

---

# Part III. What changes when there are many cells?

## 9. Two different reasons for a large total field

We now keep A and B but look at their fields together.

Before the transfer, their total field was

\[
\Phi_{\rm total}=32+4=36\ {\rm J}.
\]

After equalization, it was

\[
\Phi_{\rm total}=8+16=24\ {\rm J}.
\]

Those 36 J can therefore be separated into:

- 24 J associated with the combined shortage that redistribution cannot remove;
- 12 J associated with the uneven distribution that redistribution can remove.

This is not a new physical connection between A and B. “Total field” simply means adding their separate field values. A's local slope still depends only on A.

### Why does the remaining shortage correspond to 24 J?

The total reference is 300 J and the total resource is 180 J. Their ratio is

\[
\bar y=\frac{180}{300}=0.6.
\]

If the whole 300 J-reference system is uniformly at 60% of its reference, its field is

\[
\frac{300\ {\rm J}}2(0.6-1)^2=24\ {\rm J}.
\]

The bar in \(\bar y\) means the combined ratio. It is not the simple average of the cell percentages unless all reference amounts are equal.

Here the simple average of 20% and 80% is 50%, which would be wrong. B represents twice the reference amount of A, so it must count twice as much in the combined ratio.

### The exact many-cell identity

For any finite number of same-type cells, define

\[
X=\sum_i x_i,\qquad
X^*=\sum_i x_i^*,\qquad
\bar y=\frac{X}{X^*}.
\]

Then

\[
\boxed{
\Phi_{\rm total}
=
\underbrace{\frac{\kappa X^*}{2}(\bar y-1)^2}
_{\text{departure of the total amount from the total reference}}
+
\underbrace{\frac{\kappa}{2}
\sum_i x_i^*(y_i-\bar y)^2}
_{\text{difference between the individual cell ratios}}.
}
\]

The first part depends only on how much resource the whole collection has compared with its total reference.

The second part depends on how unevenly that resource is distributed relative to the individual references.

Read the second part one cell at a time. Compare its fraction \(y_i\) with the collection's fraction \(\bar y\); square that difference; multiply by that cell's reference amount; then add the results. A larger cell counts more because it represents more of the collection, not because we give a reward for being large.

For our original A and B, the two contributions to this unevenness are

\[
\frac{100\ {\rm J}}2(0.2-0.6)^2=8\ {\rm J},
\qquad
\frac{200\ {\rm J}}2(0.8-0.6)^2=4\ {\rm J}.
\]

Together they give the 12 J removed by the B-to-A transfer. They are not two extra rewards: they describe the same 12 J improvement already calculated from the before and after fields.

Every term in the second part is a nonnegative square. It becomes zero exactly when every \(y_i\) equals \(\bar y\).

The identity works for two cells, a thousand cells, or a million cells. The number of cells does not change the reasoning.

### A short proof, with the meaning retained

For each cell write

\[
y_i-1=(\bar y-1)+(y_i-\bar y).
\]

We have separated the cell's departure into the departure shared by the whole collection and the extra difference particular to that cell.

Square this expression and sum it with weights \(x_i^*\).

The cross terms vanish because

\[
\sum_i x_i^*(y_i-\bar y)
=X-\bar yX^*=0.
\]

The remaining two square terms give the boxed identity.

### What does this say about incentives?

If all compatible redistributions are allowed and can be funded, the largest EBU gain obtainable without changing total resource is

\[
\boxed{
E_{\rm redistribution}
=\frac{\kappa}{2W_{\mathrm{Cs}}}
\sum_i x_i^*(y_i-\bar y)^2.
}
\]

This is not a promise that actors will perform all those actions. It is the maximum field decrease available from redistribution under those assumptions.

It also gives a clear name to the phenomenon we found: **an incentive to reduce unequal provision relative to the references**.

“Spread energy equally” is a useful first intuition, but the precise rule is not equal joules everywhere. It is equal fractions of reference for these same-type cells.

## 10. Which cells should supply a requested amount?

So far we have moved resource between cells. Now suppose resource must leave the collection for use.

Assume A and B both begin at their references:

\[
x_A=100\ {\rm J},\qquad x_B=200\ {\rm J}.
\]

An actor needs 30 J in total. Let A supply \(q_A\) and B supply \(q_B\), with

\[
q_A+q_B=30\ {\rm J}.
\]

The field increase is

\[
\Delta\Phi
=\frac12K_Aq_A^2+\frac12K_Bq_B^2.
\]

Three choices illustrate the difference:

| Amount supplied by A | Amount supplied by B | Field increase |
|---:|---:|---:|
| 30 J | 0 J | 4.5 J |
| 0 J | 30 J | 2.25 J |
| 10 J | 20 J | 1.5 J |

The last choice is best. Both cells supply 10% of their reference amounts.

This is not a moral instruction that everyone must supply the same fraction. It is the minimum field cost in this specified physical comparison.

### Deriving the general result

Let all cells start at their references. They must jointly supply an amount \(Q\). We seek the smallest value of

\[
\frac12\sum_iK_iq_i^2
\quad\text{subject to}\quad
\sum_iq_i=Q.
\]

Define

\[
S_K=\sum_i\frac1{K_i}.
\]

The minimizing amounts are

\[
\boxed{
q_i=\frac{1/K_i}{S_K}\,Q,
\qquad
\Delta\Phi_{\min}=\frac{Q^2}{2S_K}.
}
\]

To verify this without an optimization shortcut, write

\[
q_i=\frac{Q}{K_iS_K}+\epsilon_i,
\qquad
\sum_i\epsilon_i=0.
\]

Substituting and expanding gives

\[
\frac12\sum_iK_iq_i^2
=\frac{Q^2}{2S_K}
+\frac12\sum_iK_i\epsilon_i^2.
\]

The second term cannot be negative. It is zero exactly for the stated allocation.

The formula describes an allowed withdrawal only while each proposed \(q_i\) can actually be supplied. If a cell would have to give more than it contains or more than its permitted withdrawal, that formula is not a feasible action. The physical restriction must then be included in the allocation problem.

For same-type cells, \(1/K_i=x_i^*/\kappa\), so

\[
q_i=\frac{x_i^*}{X^*}Q.
\]

A cell with twice the reference supplies twice as much in this optimum.

### What if the cells do not start equally supplied?

Then the starting slopes also matter.

For a small withdrawal, a cell with a higher slope has a more favorable contribution. An overfilled cell can even produce positive EBU while supplying resource, because its withdrawal reduces its imbalance.

As it supplies more, its slope falls. The relative advantages can change.

This is the precise reason for continuous adjustment: the actor can change how much the next part of the request comes from each available cell as their current slopes change.

We have described the amount selected from each cell, not how fast anything happens. The theory gives a direction of economic advantage. A separate description would be needed to predict the rate at which people respond.

For example, at one present condition the next small addition to A might produce twice the EBU of the same addition to B. That is an incentive comparison. One actor might act immediately, another might act later, and a third might have no access to A. Nothing in the factor of two tells us which of those people acts or how long the operation takes. We have calculated what they would gain from the identified change, not written a schedule for their behavior.

## 11. The same principle without assuming identical cell types

The common \(\kappa\) rule makes percentages particularly simple. But the quadratic algebra also permits cells with different specified \(K_i\).

Let

\[
X=\sum_i x_i,\qquad
X^*=\sum_i x_i^*,\qquad
S_K=\sum_i\frac1{K_i},
\qquad
\lambda=\frac{X-X^*}{S_K}.
\]

The exact identity is

\[
\boxed{
\Phi_{\rm total}
=\frac{(X-X^*)^2}{2S_K}
+\frac12\sum_i\frac{(m_i-\lambda)^2}{K_i}.
}
\]

The first term is the smallest possible field at this total resource amount if the required amounts are physically permitted.

The second is the extra field due to differences between the slopes.

The minimum occurs when

\[
m_i=\lambda
\quad\text{for every }i.
\]

This gives

\[
x_i=x_i^*+\frac{\lambda}{K_i}.
\]

Unlike the same-type case, the resulting ratios \(x_i/x_i^*\) need not agree.

### Why reciprocal \(K\) appears

Since \(m_i=K_i(x_i-x_i^*)\), we can also write

\[
x_i-x_i^*=\frac{m_i}{K_i}.
\]

At a common slope \(\lambda\), cell \(i\)'s departure from its reference is \(\lambda/K_i\). Adding those departures gives

\[
X-X^*=\lambda\sum_i\frac1{K_i}=\lambda S_K.
\]

That is why \(\lambda=(X-X^*)/S_K\). The reciprocal is not an extra economic assumption: it comes from solving the response equation for the amount.

### Proof of the field separation

Write the field as \(\tfrac12\sum_i m_i^2/K_i\). In each square substitute

\[
m_i=\lambda+(m_i-\lambda).
\]

The terms linear in \(m_i-\lambda\) add to zero because

\[
\sum_i\frac{m_i-\lambda}{K_i}
=(X-X^*)-\lambda S_K=0.
\]

The remaining terms are

\[
\Phi_{\rm total}
=\frac{\lambda^2S_K}{2}
+\frac12\sum_i\frac{(m_i-\lambda)^2}{K_i}.
\]

Substituting the expression for \(\lambda\) gives the stated identity. This proof also explains why the second term cannot be a hidden negative quantity: it is a sum of squares divided by positive numbers.

### Why include this chapter if we prefer one cell type?

It separates a strong result from a stronger interpretation.

The strong quadratic result is equal slopes.

Equal percentages follow only when the size-and-type relationship \(K_i x_i^*=\kappa\) holds with the same \(\kappa\).

We should not accidentally turn “equal percentages” into a general law for arbitrary kinds of cells.

### What about a cell reaching a physical limit?

The expression above may ask for an impossible amount, such as a negative \(x_i\), or an amount above an actual maximum.

Then that unconstrained calculation is not an allowed final state.

The remaining movable cells equalize their slopes as far as the permitted changes allow. A cell at a boundary need not share their slope, because the resource movement that would improve the field may be forbidden.

For example, if a depleted cell cannot supply another joule, an attractive mathematical direction that requires it to do so is not an available action.

This is not an extra price added to repair the theory. It is the distinction between a field value and the set of physical changes the cell permits.

# Part IV. Division and joining without an EBU loophole

## 12. Divide C into A and B

Now consider a cell C with

\[
x_C^*=300\ {\rm J},\qquad
x_C=180\ {\rm J},\qquad
K_C=\frac1{300\ {\rm J}}.
\]

Its field is 24 J.

Divide C into two same-type cells:

- A receives one third of the reference and one third of the resource.
- B receives two thirds of the reference and two thirds of the resource.

The result is

\[
x_A^*=100,\quad x_A=60,\quad K_A=1/100;
\]

\[
x_B^*=200,\quad x_B=120,\quad K_B=1/200,
\]

with amounts in joules and \(K\) in inverse joules.

A's field is 8 J. B's field is 16 J. Their sum is still 24 J.

Nothing has been gained by the division itself.

### What is preserved?

Four things have clear meanings:

1. The resource amount: \(60+120=180\).
2. The total reference: \(100+200=300\).
3. The field value: \(8+16=24\).
4. The slope: both divided cells have the original slope \(-0.4\).

This is what earlier explanations called a “neutral split.” The phrase means precisely this division with no field change and no EBU contribution.

It does not mean that every possible division is neutral.

### General rule

Choose a fraction \(0<\alpha<1\). The two resulting cells have

\[
x_A^*=\alpha x_C^*,\qquad
K_A=\frac{K_C}{\alpha},\qquad
x_A=\alpha x_C,
\]

\[
x_B^*=(1-\alpha)x_C^*,\qquad
K_B=\frac{K_C}{1-\alpha},\qquad
x_B=(1-\alpha)x_C.
\]

Substitution gives

\[
m_A=m_B=m_C,
\qquad
\Phi_A+\Phi_B=\Phi_C.
\]

For many resulting cells, choose positive fractions \(\alpha_i\) that sum to one and use the same formulas for each fraction.

### Does the next withdrawal have the same cost?

If the same total withdrawal \(q\) is shared proportionally, each resulting cell supplies \(\alpha_iq\). Summing their field changes gives exactly the original C withdrawal value.

But withdrawing all of \(q\) from only a small resulting cell is a different operation. It creates an uneven condition among the resulting cells. Its cost can be greater.

There is no contradiction:

> The division does not change the value of the same proportionally distributed physical change. It does not make every different withdrawal pattern equivalent.

This is the division law in the form we actually need.

## 13. What if we divide the resource unevenly?

Keep the reference division from the previous chapter:

\[
x_A^*=100\ {\rm J},\qquad x_B^*=200\ {\rm J}.
\]

Instead of assigning 60 J and 120 J, assign 70 J and 110 J.

The total resource remains 180 J. But the field becomes

\[
\Phi_A=\frac{30^2}{200}\ {\rm J}=4.5\ {\rm J},
\]

\[
\Phi_B=\frac{90^2}{400}\ {\rm J}=20.25\ {\rm J}.
\]

The total is 24.75 J, not 24 J.

The uneven division has added 0.75 J of imbalance. Its complete contribution is negative:

\[
E_{\rm division}
=-\frac{0.75\ {\rm J}}{W_{\mathrm{Cs}}}.
\]

Moving 10 J from A back to B restores 60 J and 120 J, and produces \(0.75\ {\rm J}/W_{\mathrm{Cs}}\).

The entire sequence earns zero net EBU.

### The suspected exploit

The loophole would be:

1. Create the unequal condition without counting its field increase.
2. Get EBU for removing that inequality.

The error is not that the repair has no value. The repair has exactly the stated value.

The error is treating the earlier opposite change as if it did not happen.

### Exact extra cost for an unequal division

Start from the proportional split and add \(q\) to A while subtracting \(q\) from B. Then

\[
\boxed{
\Phi_A+\Phi_B-\Phi_C
=\frac{K_Cq^2}{2\alpha(1-\alpha)}.
}
\]

The quantity is always nonnegative. It is zero only when \(q=0\).

If \(\alpha\) is very small, putting the same extra amount \(q\) into that small cell creates a larger disparity and a larger field increase.

This is a field consequence, not a guessed construction cost. No machine price appears in the derivation.

### What does this establish?

For these specified split operations, the imbalance after division cannot be set arbitrarily while retaining the same complete accounting.

The new resource amounts, inherited references, and inherited \(K\) values determine it.

That is the rule preventing the operation “make one cell full, another nearly empty, then earn for repairing the difference” from becoming free issuance.

## 14. Join A and B, and check what survives

For two quadratic cells, define the joined reference and response by

\[
\boxed{
x_C^*=x_A^*+x_B^*,
\qquad
\frac1{K_C}=\frac1{K_A}+\frac1{K_B}.
}
\]

The total amount is

\[
x_C=x_A+x_B.
\]

If A and B already have equal slopes, their total field equals C's field:

\[
\Phi_A+\Phi_B=\Phi_C.
\]

For our 60 J and 120 J cells, the joined C has reference 300 J, amount 180 J, and \(K_C=1/(300\ {\rm J})\). Its field is the same 24 J.

### What if their slopes differ?

There is an exact extra term:

\[
\boxed{
\Phi_A+\Phi_B
=\Phi_C+
\frac{(m_A-m_B)^2}{2(K_A+K_B)}.
}
\]

The last term measures the field associated with their difference.

For the earlier 20 J and 160 J state, it is 12 J. This is precisely the maximum redistribution gain we calculated.

Now we must distinguish two operations:

**First operation: put both cells under one name but retain their separate conditions.** A still has 20 J and B still has 160 J. The 12 J difference has not disappeared. The complete description must retain it.

**Second operation: actually permit the combined resource to reach the equal-response condition.** The 12 J difference is removed. That is a represented change with a positive contribution of \(12\ {\rm J}/W_{\mathrm{Cs}}\).

The reason for making this distinction is not terminology. It is conservation. A name does not perform the equalizing resource change.

### Does splitting and joining change \(K\) permanently?

Take a C with response \(K_C\). Divide it using fraction \(\alpha\):

\[
K_A=K_C/\alpha,\qquad
K_B=K_C/(1-\alpha).
\]

Join them:

\[
\frac1{K_{\rm joined}}
=\frac{\alpha}{K_C}+\frac{1-\alpha}{K_C}
=\frac1{K_C}.
\]

Therefore

\[
\boxed{K_{\rm joined}=K_C.}
\]

The reference also returns:

\[
\alpha x_C^*+(1-\alpha)x_C^*=x_C^*.
\]

There is no way to soften the same restored cell by repeating this round trip.

### Does the order of joining matter?

No, for these aggregate parameters. With several cells,

\[
x_C^*=\sum_i x_i^*,
\qquad
\frac1{K_C}=\sum_i\frac1{K_i}.
\]

Addition gives the same result whichever pair is joined first.

However, any differences between separate internal conditions must still be accounted for. Order-independent aggregate parameters do not authorize forgetting internal differences before they are removed.

The electrical comparison is capacitance addition for parallel capacitors. The series and parallel rules are stated together in [MIT's capacitor and circuit summary](https://ocw.mit.edu/courses/8-02-physics-ii-electricity-and-magnetism-spring-2007/0d0fd6cf993958db9fbd7738c21e51e1_summary_w05d1.pdf). Our joining rule corresponds to the addition of the quantities \(1/K_i\), not to every possible electrical connection.

## 15. Can changing cell sizes improve the field without moving resource?

This question deserves a very explicit answer because an earlier phrase made it almost impossible to understand.

We are not talking about moving a cell from Warsaw to New York.

We are asking about the following mathematical comparison:

- the amounts \(x_A\) and \(x_B\) stay where they are;
- the two reference amounts \(x_A^*\) and \(x_B^*\) change;
- their sum stays the same;
- the \(K\) values change with the reference amounts according to \(K_i x_i^*=\kappa\).

For example, return to

\[
x_A=20\ {\rm J},\qquad x_B=160\ {\rm J}.
\]

The total reference is 300 J. With references 100 J and 200 J, the total field is 36 J.

Now compare references

\[
x_A^*=\frac{100}{3}\ {\rm J},
\qquad
x_B^*=\frac{800}{3}\ {\rm J}.
\]

They still add to 300 J. Both cells are now at 60% of their new references:

\[
\frac{20}{100/3}=\frac{160}{800/3}=0.6.
\]

With the corresponding changed \(K\) values, the total field is 24 J.

### Does this give permission to declare a new reference whenever convenient?

No. That would confuse a comparison of two cell specifications with an established physical operation.

If \(x_A^*\) represents a genuine amount needed at A, reducing that number does not make the need disappear.

If a real division or joining changes which physical function each resulting cell represents, changed references may be justified. But that must be the actual operation being studied.

This is the precise question:

> Can the represented cell really be resized in this way, or have we only changed the number used to judge it?

The equation cannot answer that question by itself.

### What the mathematics does establish

For positive fixed amounts \(x_i\), fixed total reference \(X^*\), and common \(\kappa\),

\[
\Phi_{\rm total}
=\frac{\kappa}{2}
\left(
\sum_i\frac{x_i^2}{x_i^*}-2X+X^*
\right).
\]

The inequality

\[
\sum_i\frac{x_i^2}{x_i^*}\ge\frac{X^2}{X^*}
\]

can be checked by expanding the following sum of squares:

\[
\sum_i
\left(
\frac{x_i}{\sqrt{x_i^*}}
-\frac{X}{X^*}\sqrt{x_i^*}
\right)^2
=\sum_i\frac{x_i^2}{x_i^*}-\frac{X^2}{X^*}
\ge0.
\]

The sum is zero exactly when all its squared terms are zero. Therefore, for positive \(x_i\), the smallest field occurs when

\[
\boxed{x_i^*=\frac{X^*}{X}x_i.}
\]

In plain language: the reference assigned to each cell is proportional to the resource it contains.

This yields the same minimum total field as redistributing resource proportionally to fixed references. But the two procedures change different things.

One moves resource toward fixed references. The other changes references around fixed resource amounts.

The second procedure is not automatically an acceptable substitute for the first.

If a cell has no resource, the formal proportional assignment asks for a zero reference. That falls outside our positive-reference cell definition. We cannot use this calculation as permission to erase an unsupplied cell and its represented requirement.

### A useful conservation check

If a reference or \(K\) actually changes, the complete field differential is

\[
d\Phi
=m\,dx
-m\,dx^*
+\frac12(x-x^*)^2\,dK.
\]

The usual \(-m\,dx/W_{\mathrm{Cs}}\) contribution alone no longer describes the complete field change.

This is why changing \(x^*\) cannot be an invisible operation. The calculation must describe the reference change as well as the resource change, without automatically attributing it to whoever benefits.

We have found a conditional mathematical result, not a new automatic reward for changing reference numbers.

# Part V. People, payments, and conservation

## 16. How can both participants benefit from an exchange?

In the B-to-A transfer, B's contribution consumed \(12\ {\rm J}/W_{\mathrm{Cs}}\), while A's produced \(24\ {\rm J}/W_{\mathrm{Cs}}\).

Why would the person supplying from B agree?

Suppose the person handling the A contribution transfers existing EBU to the B participant. Let the payment be \(P_{\mathrm{EBU}}\).

Measured on the same EBU scale, any payment satisfying

\[
\frac{12\ {\rm J}}{W_{\mathrm{Cs}}}
<P_{\mathrm{EBU}}<
\frac{24\ {\rm J}}{W_{\mathrm{Cs}}}
\]

leaves both better off relative to their individual signed contributions.

For example, a payment of \(18\ {\rm J}/W_{\mathrm{Cs}}\) gives:

- B participant: \(-12+18=+6\) J-equivalent of EBU.
- A participant: \(+24-18=+6\) J-equivalent of EBU.

The total remains 12 J-equivalent. The transfer divides that gain; it does not create a second gain.

### A general cooperation result

Suppose one part of an allowed operation costs \(D\) EBU and another earns \(R\) EBU, with \(R>D\).

Then a payment

\[
D<P_{\mathrm{EBU}}<R
\]

makes both participants' net EBU changes positive.

This is an exact reason why cooperation can be attractive under EBU gain incentives.

It is not a guarantee that the people know the opportunity, can fund the required negative contribution, or will agree to a particular split.

Those practical choices matter to what actually occurs, but they do not remove the positive total available in the operation.

For example, if the negative part must be paid before the positive part is completed, someone needs existing available EBU for that earlier payment. The expected later gain is not already an existing token. An arrangement that settles the identified parts together is another possibility to specify, not an automatic permission to spend the same units twice.

### Existing-token movement is not field movement

When the 18 J-equivalent payment occurs:

- one account loses that amount;
- the other gains that amount;
- neither cell's resource changes because of the payment itself;
- the total circulating EBU does not change.

This is the specific economic interaction between independent cells and actors. Payments can make a physical action attractive to a participant without making the payment a second physical contribution.

There is no need to invent a new mechanical force between A and B merely because the people exchange tokens.

### A positive result for one person is not always a gain for everyone together

The conservation law adds every participant's signed result. It does not require each person's result to be the same.

Suppose one person pays EBU to create an imbalance, and another later earns EBU by removing it. The second person can finish with more EBU. That does not contradict the zero complete value of the two-action cycle: the first person paid the corresponding amount.

Existing-token payments can change the distribution between the people again. They still cannot change the complete total.

This distinction matters when we say that an actor “wants to earn more EBU.” For the complete B-to-A operation, the 12 J-equivalent increase is fixed by the field. Which participant receives how much of that increase depends on the identified contributions and the payments they agree to make. The field establishes the complete opportunity; it does not specify every person's agreement.

## 17. Several actors changing the same cell

A million cells are not the only complication. Many actors may act on one cell.

Let A currently be \(d\) below its reference. Two actors add \(q_1\) and \(q_2\).

If each is separately promised the finite value calculated as if the other did not exist, the two quoted numerators are

\[
K_A(dq_1-q_1^2/2),
\qquad
K_A(dq_2-q_2^2/2).
\]

But the actual complete addition is \(q_1+q_2\), whose field improvement is

\[
K_A\left[d(q_1+q_2)-\frac12(q_1+q_2)^2\right].
\]

The two isolated quotes exceed this actual amount by

\[
K_Aq_1q_2.
\]

That is the error from treating the same starting condition as unchanged during both finite additions.

### How the current-field rule avoids it

At the actual current condition, use the same slope for all identified small changes:

\[
dE_1=-\frac{m_A\,dx_1}{W_{\mathrm{Cs}}},
\qquad
dE_2=-\frac{m_A\,dx_2}{W_{\mathrm{Cs}}}.
\]

Since the actual total change is

\[
dx_A=dx_1+dx_2,
\]

we get

\[
\boxed{
dE_1+dE_2
=-\frac{m_A\,dx_A}{W_{\mathrm{Cs}}}
=-\frac{d\Phi_A}{W_{\mathrm{Cs}}}.
}
\]

The same reasoning applies to any finite number of identified contributors.

If two people perform one inseparable operation through a single responsible entity, the model can identify that entity's contribution. It need not invent separate physical shares for every person involved.

### Does this settle who gets what from endpoints alone?

No. The before and after field values give the complete amount. They do not, by themselves, reconstruct each person's part.

In our ideal study, the relevant contributions are identified as the changes occur. This is the assumption that lets the mathematical sum correspond to the actual participants without duplication.

This is not a new uncertainty about the conservation law. It is the information required to apply that law to separate accounts.

### A numerical example without any guessed personal share

Return to A at 20 J with reference 100 J and \(K_A=1/(100\ {\rm J})\). Anna adds 10 J and Bob adds 10 J. The complete change is 20 J to 40 J, which produces \(14\ {\rm J}/W_{\mathrm{Cs}}\).

Compare three ways the identified additions can occur:

| Actual additions | Anna's field-decrease contribution | Bob's field-decrease contribution | Complete total |
|---|---:|---:|---:|
| Anna supplies her 10 J, then Bob supplies his 10 J | 7.5 J | 6.5 J | 14 J |
| Bob supplies his 10 J, then Anna supplies her 10 J | 6.5 J | 7.5 J | 14 J |
| Each supplies half of every actual small increase | 7 J | 7 J | 14 J |

Divide the entries by \(W_{\mathrm{Cs}}\) to express them in EBU.

The third row does not assume a clock speed. It says that whenever A's amount increases by \(dx_A\), Anna's identified part is \(dx_A/2\) and Bob's is \(dx_A/2\). Each receives half of the current contribution at every step, so each total is half of 14.

The first contributor in the first two rows meets a more depleted A. That is why the contributions differ. In every row the exact current-field rule gives the same complete 14, while retaining who actually supplied each part.

If both instead used the untouched starting condition for their separate 10 J quotes, each would claim 7.5 J-equivalent. Their 15 J total would exceed the actual 14 J improvement. The missing 1 J is precisely \(K_Aq_1q_2\).

Separate measurements are an assumption of this ideal example. If Anna and Bob form one entity that performs one identified addition, the book can value that entity's complete addition without deciding how it divides its proceeds internally.

## 18. What is actually conserved?

Let

\[
\Phi_{\rm total}=\sum_i\Phi_i
\]

and let \(G\) be the total existing EBU in the modeled accounts.

Consider an ideal completed update in which every relevant field change has exactly one matching signed EBU contribution. Then

\[
W_{\mathrm{Cs}}\Delta G=-\Delta\Phi_{\rm total}.
\]

Rearranging:

\[
\boxed{
W_{\mathrm{Cs}}G+\Phi_{\rm total}=\mathcal B,
}
\]

where \(\mathcal B\) is the constant established by the initial complete condition. The different letter style distinguishes this constant from the cell named B.

Equivalently,

\[
G+\frac{\Phi_{\rm total}}{W_{\mathrm{Cs}}}
=\text{constant}.
\]

### Read the equation in words

If represented imbalance falls by 10 J, the matching account total rises by \(10\ {\rm J}/W_{\mathrm{Cs}}\).

If imbalance rises by 10 J, the matching account total falls by the same number of EBU.

The two sides move oppositely.

This is the precise meaning of EBU as a mirror of field improvement. It is not the statement that circulating EBU equals the physical energy stored in all resources.

### What happens when people pay each other?

Their total \(G\) does not change, and the cells do not change. The equation remains true.

### What happens if choices are poor?

The identity still holds for correctly counted allowed changes. A poor choice can increase the field and consume EBU. A good choice can decrease it and produce EBU.

Conservation is not conditional on people making the best choice.

If we additionally require \(G\ge0\), then

\[
\Phi_{\rm total}\le\mathcal B.
\]

The whole collection cannot reach a greater field value than its total budget permits within these premises.

### Does this protect every cell from depletion?

Not automatically.

The field at zero amount in cell \(i\) is

\[
\Phi_i(0)=\frac12K_i(x_i^*)^2.
\]

This is finite for the quadratic field.

If

\[
\mathcal B<\frac12K_i(x_i^*)^2,
\]

then cell \(i\) cannot be empty in any modeled fully funded state: its field alone would exceed the whole budget.

But if the total budget is larger, the global bound does not by itself prohibit that cell from emptying. Improvement elsewhere can supply the EBU used for its deterioration.

Thus we have a strong global accounting restriction and a precise sufficient condition for excluding a particular state. We do not have an automatic infinite barrier at every cell.

### Why completed updates matter here

The book follows the owner's ideal of evaluating actual physical contributions and updating accounts by the exact completed amount.

If an action is allowed to pass through an unfunded intermediate condition before its final settlement, the final identity alone does not prove a funding restriction at every intermediate point.

To claim that stronger protection, funding and complete accounting must hold at each physical stage to which the bound is applied.

Older project documents also study accepted amounts before fulfillment. That is a distinct accounting convention with additional terms. This book does not silently rewrite it; its ideal accounting premise is stated here and retained throughout.

## 19. What happens at perfect balance?

Suppose every cell is exactly at its reference. Then

\[
\Phi_{\rm total}=0.
\]

If the modeled circulating amount is also \(G=0\), the conserved quantity is \(\mathcal B=0\).

Under nonnegative holdings and the exact accounting rule, a finite action that creates positive imbalance cannot be funded.

This explains the startup issue we discussed. Perfect balance with no EBU is not automatically a functioning economy with funded withdrawals.

One way to obtain EBU within the rule is to begin with a specified positive imbalance and perform actual restoration. Another possibility would be a separately specified initial account allocation or opening condition. Such a choice changes the initial \(\mathcal B\); it is not derived merely by naming the reference.

### Can there be repeated use and restoration?

Yes, at the accounting level.

Start with a funded withdrawal from a cell at reference. The withdrawal increases its field and consumes EBU. Later restore the same resource amount, returning it to the same reference condition. The restoration decreases the field and produces the same EBU amount.

The total signed contribution around the cycle is zero.

This does not mean nothing useful happened. Resource could have been used between withdrawal and restoration. It means that the field and matching account total returned to their initial values.

Whether the physical resource can truly be renewed or replaced is a different question. The EBU identity cannot create an external energy supply or undo irreversible material losses.

### What if restoration uses new renewable input?

If the represented cell returns to the same amount, its field can return to the same value regardless of whether the resource was recovered from the earlier use or supplied from a renewable source.

The field sees the represented resource change. It does not require an individual joule to return as the same identifiable object.

But a claim about the entire spaceship must include the relevant physical balances and limitations of its renewal process. The token cycle alone proves neither perpetual operation nor a replenishment rate.

**Cycle law:** returning the complete modeled condition to its beginning returns the complete signed EBU total to zero. Real repeated activity is compatible with this law; perpetual physical supply does not follow from it.

---

# Part VI. Arrangements of cells: what topology can and cannot change

## 20. There are three different maps

The word “topology” can sound mysterious. Here it begins with a simple question:

> Which operations can happen between which objects?

There are three maps we must not confuse.

### Map one: possible resource movements

Suppose an actor can move resource directly between A and B, and directly between B and C, but not directly between A and C.

We can draw

\[
A\longleftrightarrow B\longleftrightarrow C.
\]

The lines describe possible actor-mediated resource movements. They are not wires making A's local field depend on B's amount.

If C changes by itself, A's slope is still

\[
m_A=K_A(x_A-x_A^*).
\]

The map changes which actions are available, not this local formula.

### Map two: possible EBU payments

People may be able to transfer existing EBU even when they cannot directly move resource between their cells.

This is a different map. A payment route does not automatically transport the physical resource.

It can nevertheless matter greatly: a participant who would otherwise bear a negative contribution can be compensated by someone receiving a larger positive contribution.

### Map three: the history or description of division

C might have been divided into A and B. Later A might be divided into A1 and A2.

That gives a branching description:

\[
C\ \rightarrow\ \{A,B\},
\qquad
A\ \rightarrow\ \{A1,A2\}.
\]

It tells us how references and response factors are inherited. It does not automatically tell us who can deliver resource to whom, or who can pay whom.

These three maps can differ.

This distinction is particularly important for our project because cells remain independent and actors create the economic interactions. A diagram must not silently replace that design with a mechanically coupled circuit.

## 21. A line, a ring, a star, and all-to-all access

Take four unchanged cells A, B, C, and D. Consider four ways actors might be able to move resource.

**Line:** A–B–C–D.

**Ring:** A–B–C–D–A.

**Star:** A connects directly to B, C, and D, while those three have no direct connections to each other.

**All-to-all:** every pair permits a direct movement.

If the resource amounts, references, and \(K\) values are unchanged, all four arrangements have the same immediate total field.

So changing the arrangement alone does not produce EBU under the local field rule.

What can change is the set of operations through which actors can reach a better distribution.

### Reachable final balance

Assume all connections allow either direction, resource is compatible, the equal-slope target and required intermediate states are permitted, and the necessary signed contributions can be funded.

If the map is connected, every cell can be reached from every other through some sequence. The same equal-slope final distribution is then reachable, even when direct pair movements are restricted.

The route and intermediate conditions can differ greatly.

A line can require several handoffs. A star can make the center a common intermediary. A ring gives an alternative route. All-to-all access avoids the need for intermediaries for a single pair transfer.

Those differences matter to the amount handled, to funding along the way, and to which participants must cooperate.

They do not automatically change the complete EBU value of reaching the same final cell conditions.

### One shipment through four arrangements

For this comparison, take four same-type cells, each with reference 100 J and \(K=1/(100\ {\rm J})\). A contains 140 J, D contains 60 J, and B and C each contain 100 J.

A has 40 J above its reference. D has 40 J below. Moving those 40 J from A to D restores all four cells to their references.

The starting field is

\[
\Phi_{\rm total}
=\frac{40^2}{200}\ {\rm J}
+\frac{40^2}{200}\ {\rm J}
=16\ {\rm J}.
\]

The final field is zero. Every complete permitted route that produces exactly these final conditions therefore earns \(16\ {\rm J}/W_{\mathrm{Cs}}\).

But the amount handled across connections can differ:

| Arrangement | Shortest allowed route for this shipment | Amount handled |
|---|---|---:|
| Line A–B–C–D | A→B→C→D | 120 J |
| Ring A–B–C–D–A | A→D | 40 J |
| Star centered on A | A→D | 40 J |
| All-to-all | A→D | 40 J |

Here “120 J handled” means that 40 J crosses three connections. It does not mean that 120 J was consumed or destroyed.

Does the star always improve on the line? No. In a different starting scenario, let B contain 140 J and C contain 60 J, with A and D at reference. Moving 40 J from B to C takes one connection on the line, but two on the star centered on A: B→A→C.

The best arrangement depends on which operations must be performed. The fields alone do not designate one cell as the universal best center.

### What if no neighboring exchange offers any positive gain?

There is a useful exact conclusion when every sufficiently small neighboring exchange is allowed in both directions.

If neighboring cells A and B had different slopes, moving a small amount from the higher slope to the lower one would produce positive EBU. Therefore, if neither direction can improve the field, their slopes must be equal.

On a connected map, repeating this argument along the connections forces every cell to have the same slope, say \(\lambda\).

Now compare any other condition with the same total resource. Write its changes as \(\epsilon_i\), with \(\sum_i\epsilon_i=0\). The field difference from the equal-slope condition is

\[
\Delta\Phi
=\lambda\sum_i\epsilon_i
+\frac12\sum_iK_i\epsilon_i^2
=\frac12\sum_iK_i\epsilon_i^2
\ge0.
\]

Thus this condition is the unique smallest-field distribution at that total resource amount, if it is permitted.

This gives a local check of a completed balance: on a connected map, equal neighboring responses certify the global fixed-total minimum.

It does not say how actors get there, or that the best sequence for every limited amount of handling is obtained by a greedy rule. Chapter 27 will show why those are different claims.

If an exchange is blocked by a physical restriction or cannot be funded, absence of an executed exchange does not establish equal slopes. The test requires that the compared exchanges really be available.

### No automatic penalty for being a center

The current field has no built-in fee for “being the hub.”

If the center receives and later sends resource, its actual field changes count. If it ends where it began, those changes cancel in the complete total.

If it retains excess or suffers a shortage, its final field reflects that.

To claim that more operations through the center cause an additional physical change, we would have to state what that change is and include it in the model. We will not invent one here.

## 22. The resource conservation law at a group boundary

Take a group of cells inside a drawn boundary. Some actor movements occur between cells inside the group. Others cross the boundary.

An internal movement subtracts resource from one cell and adds it to another within the same group. It does not change the group's total.

Therefore:

\[
\boxed{
\text{change of resource inside the group}
=
\text{resource brought in}
-
\text{resource taken out}.
}
\]

This is true for a two-cell group or a million-cell group.

It is a useful Kirchhoff-like conservation statement. Electrical circuit theory uses an analogous balance of charge at junctions. Here we are balancing identified resource amounts, not introducing a law of current per second.

### The same statement in compact notation

Give each allowed connection an arbitrary positive direction. Let \(df_e\) be the signed resource moved on connection \(e\).

For a movement from cell \(a\) to cell \(b\),

\[
dx_a=-df_e,\qquad dx_b=+df_e.
\]

The EBU contribution is

\[
dE_e=\frac{(m_a-m_b)\,df_e}{W_{\mathrm{Cs}}}.
\]

Adding all actual connection movements gives

\[
\boxed{
\sum_e dE_e
=-\frac1{W_{\mathrm{Cs}}}\sum_i m_i\,dx_i
=-\frac{d\Phi_{\rm total}}{W_{\mathrm{Cs}}}.
}
\]

Every removal and addition is counted once. This is the conservation check for arbitrary simultaneous allowed movements.

### Going around a loop

At one fixed current condition, consider the slope differences around A→B→C→A:

\[
(m_A-m_B)+(m_B-m_C)+(m_C-m_A)=0.
\]

The intermediate slopes cancel.

For a finite sequence the slopes change, so we must integrate the actual contributions. If the complete cell condition returns to its start, the total signed EBU remains zero.

Thus a loop is not an EBU generator merely because it has several connections.

Chapter 40 develops these statements alongside the separate balance law for token payments, with numerical examples, proofs, and a consequence for the directions that currently offer positive EBU contributions.

## 23. What if part of the economy cannot exchange with the rest?

Suppose A and B form one accessible group, while C and D form another. There is no allowed resource movement between the groups.

Each group can equalize internally. But their combined resource amounts cannot change through internal exchange.

One group may remain uniformly well supplied while the other remains uniformly depleted.

There is then a difference that cannot be repaired using the existing movements.

### Exact value of the remaining difference

For each accessible group \(c\), define its total reference \(X_c^*\), total resource \(X_c\), and ratio

\[
\bar y_c=X_c/X_c^*.
\]

After each group has equalized internally, the total field is

\[
\Phi_{\rm separated}
=\frac{\kappa}{2}\sum_cX_c^*(\bar y_c-1)^2.
\]

If the groups can exchange and reach a common ratio \(\bar y\), the minimum is

\[
\Phi_{\rm connected}
=\frac{\kappa X^*}{2}(\bar y-1)^2.
\]

Their difference is

\[
\boxed{
\Phi_{\rm separated}-\Phi_{\rm connected}
=\frac{\kappa}{2}\sum_cX_c^*(\bar y_c-\bar y)^2.
}
\]

This is the field improvement that access between the groups could make possible.

It is the same unevenness identity, now applied to groups rather than individual cells.

### Does creating the connection earn that amount immediately?

No. Access makes the action possible. The actual resource movements produce the actual field changes.

This is a clean separation:

- a new possible route can unlock an opportunity;
- using the route to improve the represented conditions realizes the field contribution.

We should not count the same improvement once for opening the route and again for moving the resource.

### A new monotonicity result

If we add an allowed movement while keeping every old movement available, the best attainable field improvement cannot become worse.

Proof: every old plan is still allowed. The expanded set of plans contains the old set. Its best result therefore cannot be inferior.

This is a statement about the best available result, not a guarantee about what self-interested actors actually choose.

There is a related physical pattern in Rayleigh's electrical-network monotonicity law: making electrical connections easier cannot increase the corresponding effective resistance. The electrical result concerns a different quantity and has its own premises; [Doyle and Snell, sections 1.3–1.4](https://math.dartmouth.edu/~doyle/docs/walks/walks.pdf), give the energy-based derivation.

## 24. The route can require effort even when the EBU total is unchanged

Return to A–B–C. Suppose the intended final change is:

\[
x_A\mapsto x_A-q,\qquad
x_B\mapsto x_B,\qquad
x_C\mapsto x_C+q.
\]

B is an intermediary. It finishes with the same amount as before.

The complete field contribution is

\[
E=
\frac{
\Phi_A(\text{before})-\Phi_A(\text{after})
+\Phi_C(\text{before})-\Phi_C(\text{after})
}{W_{\mathrm{Cs}}}.
\]

B's beginning and ending field values cancel.

If an allowed direct A→C movement produces exactly those same final conditions, its complete EBU amount is identical.

### Does that mean the routes are physically identical?

No.

On the direct route, \(q\) is moved once.

On A→B→C, \(q\) crosses two connections. The total amount handled across connections is \(2q\).

We have two different measurements:

1. Field improvement, which determines complete signed EBU here.
2. Total resource handling along the chosen route.

The current independent-cell field distinguishes them only if the route leaves additional represented changes. It does not automatically charge for every handoff.

This is an important result, not a reason to invent a distance fee.

### An intermediary can need compensation

Suppose the current slopes are

\[
m_A=1,\qquad m_B=2,\qquad m_C=0.
\]

A small A→B movement has contribution

\[
(1-2)dq/W_{\mathrm{Cs}}<0.
\]

A corresponding B→C movement has contribution

\[
(2-0)dq/W_{\mathrm{Cs}}>0.
\]

Together they give

\[
(1-0)dq/W_{\mathrm{Cs}}>0.
\]

The complete operation is beneficial even though one part is negative.

This is exactly where economic cooperation and transfers of existing EBU become relevant. An actor who refuses every individually negative part may prevent a positive complete operation unless there is compensation or a common responsible entity.

It is not necessary for the intermediary cell's field to become mechanically coupled to the other cells. The coupling is in the permitted operation and its financing.

## 25. A precise shortest-route law

We can prove a shortest-route result, but we must say what is being minimized.

Here we minimize the total resource amount handled across connections. For equal handling weights, a quantity \(q\) sent through three connections counts as \(3q\).

More generally, give each connection a specified positive weight \(w_e\). These weights describe the chosen physical-progress measurement. They are not extra EBU charges.

For a path of operations define

\[
S_{\mathrm{move}}=\sum_e\int w_e\,|df_e|.
\]

The absolute value means that sending resource forward and then back counts as two movements, not zero handling.

Let \(d(A,C)\) be the smallest sum of weights along a route from A to C.

For the final shipment of \(q\) from A to C, with all other cells restored to their starting amounts,

\[
\boxed{S_{\mathrm{move}}\ge q\,d(A,C).}
\]

A shortest route attains this bound if the physical states and funding needed along it are allowed.

### Why the bound is true

Label each cell \(v\) by its shortest weighted distance \(h_v\) from A.

Across a connection from \(a\) to \(b\),

\[
|h_b-h_a|\le w_e.
\]

Every resource movement can change the distance-weighted amount by at most its weighted handling.

The complete final shipment increases that distance-weighted amount by exactly \(q\,d(A,C)\). Therefore the total handling cannot be smaller.

This argument permits many simultaneous routes, loops, and reversals. None can beat the bound.

The graph mathematics of route costs, paths, and cycles is developed in [MIT's minimum-cost-flow notes](https://courses.csail.mit.edu/6.854/20/Notes/n09-mincostflow.html). Our field-value calculation is separate from those independently specified route weights.

### Does EBU gain alone force the shortest route?

Not in the current endpoint-only comparison.

If two allowed routes have the same complete final cell conditions, their complete signed EBU contributions are equal. One may nevertheless handle more resource.

The conservation law cannot both make complete field value independent of route and, without another represented difference, award different EBU totals solely for taking those two routes.

This identifies a precise limit of the current incentive:

> It rewards the represented improvement. It does not distinguish two ways of producing exactly the same complete represented change unless something relevant differs between them.

That does not refute the least-resource result for choosing which cells to improve. It separates that result from geographic or logistical routing.

# Part VII. Continuous adjustment and the least-resource principle

## 26. A positive theorem when every pair is available

There is an important setting in which choosing the best current exchange does produce the best field result for a given amount transferred.

Assume:

- the cells have fixed independent quadratic fields;
- compatible resource can move directly between any pair;
- each joule transferred is counted once, regardless of the selected pair;
- the transfers considered are physically permitted and can be funded;
- the actor can continuously adjust the selected donor and receiver;
- splitting and joining are not occurring during this action.

Let \(P\) be the total amount transferred.

At each small step, choose a cell with the highest current slope as donor and one with the lowest current slope as receiver.

The next gain per transferred joule is

\[
\frac{m_{\rm highest}-m_{\rm lowest}}{W_{\mathrm{Cs}}}.
\]

As the donor supplies resource, its slope falls. As the receiver accepts it, its slope rises.

When another cell ties for highest or lowest, the transfer can be shared among the tied cells so that their slopes remain tied.

This gives the following result:

> Until equalization is reached, this continuously adjusted exchange achieves the largest total field reduction available for each transferred amount \(P\).

Consequently, it uses the least transferred amount to reach any attainable field-reduction target in that range.

### Why this is stronger than “the next step looks good”

The positive result rests on the fact that the best final allocations for successive values of \(P\) fit together.

As \(P\) grows:

- cells initially above the decreasing donor slope level only give resource;
- cells initially below the increasing receiver slope level only receive resource;
- cells between those levels remain unchanged until reached.

No earlier transfer needs to be reversed before equalization.

This is why one continuously adjusting path can be best at every intermediate transferred amount in this class.

### A formula for the two moving slope levels

Let \(m_i^0\) be the starting slopes. Choose levels \(u\ge\ell\) such that

\[
\sum_i\max\left(\frac{m_i^0-u}{K_i},0\right)=P,
\]

\[
\sum_i\max\left(\frac{\ell-m_i^0}{K_i},0\right)=P.
\]

The first equation says that the donor cells supply \(P\) in total.

The second says that the receiver cells receive \(P\) in total.

Each donor finishes at slope \(u\). Each receiver finishes at slope \(\ell\). Cells between those levels do not change.

The construction stops when \(u=\ell\), the common equilibrium slope.

Appendix A gives a proof that no other distribution achieved using at most \(P\) can have a smaller field.

### How much must move before this improvement is complete?

Let \(\lambda\) be the common final slope from Chapter 11. The equalized amount in cell \(i\) is

\[
x_i^{\rm eq}=x_i^*+\frac{\lambda}{K_i}.
\]

The superscript “eq” means the equalized condition at the collection's current total amount. It is not necessarily the cell's own zero-imbalance reference \(x_i^*\).

When this equalized condition is permitted, the least total direct transfer needed to reach it is

\[
\boxed{
P_{\rm eq}=\frac12\sum_i|x_i^0-x_i^{\rm eq}|.
}
\]

Why the half? A transferred joule repairs one joule of excess relative to this destination at the donor and one joule of shortage at the receiver. The sum counts that same moved joule at both ends. No path can move less than the total donor excess, and direct donor-to-receiver transfers attain that amount.

In our continuing example, A starts at 20 J and must reach 60 J; B starts at 160 J and must reach 120 J. Thus

\[
P_{\rm eq}=\frac12(40+40)\ {\rm J}=40\ {\rm J}.
\]

Moving those 40 J removes 12 J of field. The 40 J is the amount transferred; the 12 J is the field improvement; \(12\ {\rm J}/W_{\mathrm{Cs}}\) is the complete EBU contribution. They answer three different questions about the same operation.

### What this says about an actor

For one actor responsible for the complete operation, maximizing the signed physical EBU contribution is the same comparison as maximizing the field decrease.

For several actors, their complete contributions still sum to that decrease. Whether their private agreements make them select the maximizing operation is a further question. The cooperation calculation in Chapter 16 gives one exact way positive total gains can be shared.

We should retain the positive theorem without replacing its premises by the claim that every conceivable private strategy on every network is optimal.

## 27. Why a restricted arrangement requires another check

Now restrict the allowed movements to neighboring cells on a line.

The local fields remain exactly the same. Conservation remains exactly the same.

But the set of available actions has changed.

A very attractive donor and receiver may be separated by intermediate cells. The best next neighboring transfer can alter which later routes are attractive. A transfer that seemed useful at a small handling budget may need to be partly reversed to achieve the best result at a larger budget.

This is not the fixed-action mistake we discussed earlier. Continuous adjustment is still allowed. The issue is whether the best results at different budgets fit along one path without extra reversals.

### An exact mathematical example

Take five cells on a line:

\[
1-2-3-4-5.
\]

All have reference 10 J and \(K=1/{\rm J}\). This is a separate same-type example with \(\kappa=10\); the value does not vary between its five cells. Their initial amounts are

\[
(10,14,9,12,14)\ {\rm J}.
\]

They all have positive resource. No split, merge, moving reference, or extra interaction term is involved.

Count one joule moved across one connection as one joule of handling.

The best final result with 3 J of total handling requires net movements, in the four left-to-right connection directions,

\[
\left(-\frac57,\frac{17}{14},-\frac12,-\frac47\right)\ {\rm J}.
\]

The best final result with 4 J of total handling requires

\[
(-1,1,-1,-1)\ {\rm J}.
\]

A negative entry means movement to the left.

To go from the first set of net movements to the second requires at least

\[
\frac{10}{7}\ {\rm J}
\]

of additional handling.

But only 1 J remains between budgets 3 J and 4 J.

Therefore no one path can be best at both budgets. In particular, no continuously greedy rule can be universally best at every budget on every such arrangement.

Appendix B proves both optimal endpoints and the distance between them. This is a written counterexample, not a simulation result.

### What survived the check?

All the core field identities survive:

- actual contributions still sum to the complete field change;
- returning to the same complete condition still has zero net EBU;
- positive transfers still reduce the field;
- equal slopes still characterize an interior fixed-total optimum;
- the all-pair theorem still holds under its stated assumptions.

What fails is the unrestricted extension: “the same local rule is globally least-resource for every possible topology.”

Finding this boundary is useful. It tells us exactly what a future theorem must specify about access and the measurement of resource progress.

## 28. What remains of the Fermat comparison?

In optics, a path is evaluated by a particular accumulated quantity: travel time or optical path length in the usual stationary-medium formulation. It is not generally the shortest geometric line. [Feynman's presentation of reflection and refraction](https://www.feynmanlectures.caltech.edu/I_26.html) shows why the chosen quantity matters.

For EBU, we must likewise name the path measurement.

In Chapter 26 it was the total amount transferred between directly accessible pairs.

In Chapter 25 it was the total weighted handling across a particular graph.

Those are not automatically the same measurement.

The EBU field provides the improvement being sought. The path measurement provides the resource used to achieve it.

The productive analogy is therefore:

| Optical comparison | EBU path comparison |
|---|---|
| Specified starting and ending conditions | Specified initial cells and desired field improvement or final state |
| Allowed optical paths | Allowed physical resource operations |
| Accumulated optical path or travel time | Explicitly specified resource-progress measurement |
| A variational or minimum-path result under its premises | A proved least-resource result under the cell and access premises |

The analogy does not require calling resource progress clock time. It requires making the comparison precise.

### A useful general sufficient condition

Suppose a specified progress quantity is \(s\), and let

\[
z=\Phi_{\rm total}
\]

be the current field level.

Assume every allowed action satisfies

\[
-\frac{dz}{ds}\le a(z),
\]

where \(a(z)>0\) depends only on the current field level. The bound must hold over every field level visited by the competing paths, not just along a favored route. We consider paths accumulated from the stated small changes, with no uncounted jumps.

Suppose an allowed continuously adjusted path can attain equality throughout the range of interest. If \(s\) is measured in joules of resource progress, \(a(z)\) is dimensionless; more generally its units are field-joules per unit of the chosen progress measurement. It is not a clock rate.

Then any path from \(z_0\) to a lower \(z_1\) requires at least

\[
\boxed{
s_{\min}\ge
\int_{z_1}^{z_0}\frac{dz}{a(z)}.
}
\]

The path attaining equality achieves the bound.

If \(a(z)\) tends to zero at the target, the target must be treated by a limit of this integral. A divergent integral would rule out reaching that target with finite progress under these premises.

To see this, define a transformed field

\[
F(z)=\int^z\frac{du}{a(u)}.
\]

The local inequality gives \(-dF/ds\le1\). Integrating gives the result, even if a competing path makes detours within the stated domain.

This condition is powerful because it turns a local bound into a complete path bound.

But the function \(a(z)\) and its attainability must be established for the actual action set. Independent quadratic cells on an arbitrary restricted graph do not automatically satisfy the required relationship.

**The correct conclusion:** least-resource behavior is a meaningful, provable question within EBU. It is not a substitute name for conservation, and conservation alone does not settle every path problem.

---

# Part VIII. Repeated division, growth, and constants

## 29. A large cell divided again and again

Suppose C is divided into A and B. Then A is divided into A1 and A2. Then one of those is divided again.

If every division follows the proportional rule, the final pieces all retain the original fraction of reference:

\[
\frac{x_i}{x_i^*}=\frac{x_C}{x_C^*}.
\]

Their slopes are therefore all the original slope. Their fields sum to the original field.

It does not matter whether we divide into two pieces first and then divide those, or divide directly into the final collection.

For example, divide C into fractions \(1/3\) and \(2/3\), then divide the first fraction in half. The final fractions are

\[
\frac16,\quad\frac16,\quad\frac23.
\]

These sum to one. Each final \(K_i\) is \(K_C\) divided by its fraction.

Joining the pieces restores

\[
\frac1{K_C}=\sum_i\frac1{K_i}.
\]

The history of the proportional divisions does not alter the restored aggregate.

### What changes if the pieces later act independently?

After division, different actors may withdraw from different pieces. Their ratios can diverge.

That divergence is a real change of the represented resource distribution. It is not a consequence of the cell names.

The division creates the possibility of separate conditions. Later actions create the actual differences.

This explains why division can be economically relevant without awarding EBU merely for division: it can change who can operate which part, where operations are available, and which later distributions are possible.

These practical possibilities must be specified in the operation set. The quadratic field does not select a preferred number of pieces on its own.

## 30. A complete field can be described at several scales

Imagine four cells. First compare the two cells in the left pair. Then the two in the right pair. Finally compare the left pair with the right pair.

There is an exact way to add these differences without counting anything twice.

For any group \(g\), define

\[
x_g^*=\sum_{i\in g}x_i^*,
\qquad
x_g=\sum_{i\in g}x_i,
\qquad
y_g=\frac{x_g}{x_g^*}.
\]

Suppose a group is divided into two subgroups L and R. Then

\[
x_g^*=x_L^*+x_R^*,
\qquad
y_g=\frac{x_L^*y_L+x_R^*y_R}{x_L^*+x_R^*}.
\]

The difference between the two subgroup ratios contributes

\[
\frac{\kappa x_L^*x_R^*}
{2(x_L^*+x_R^*)}(y_L-y_R)^2.
\]

Applying this at every division gives

\[
\boxed{
\Phi_{\rm total}
=
\frac{\kappa x_{\rm whole}^*}{2}(y_{\rm whole}-1)^2
+
\sum_{\text{divisions }g}
\frac{\kappa x_L^*x_R^*}
{2(x_L^*+x_R^*)}(y_L-y_R)^2.
}
\]

The first term describes the whole collection's departure from its total reference.

Each term in the sum describes a difference at one level of the grouping.

### Why is this useful?

It answers the fear that joining everything into one giant cell might hide the important imbalance.

If we retain only the first term, we do hide differences.

If we retain the first term and all the subgroup terms, the description is exact. We have organized the same information; we have not removed it.

An actual equalizing operation can reduce one or more of those terms. Merely drawing another grouping tree cannot reduce the complete sum.

### Does a different tree give a different EBU total?

No. The tree changes which differences are represented at each level, but the complete sum always equals \(\sum_i\Phi_i\).

This is a useful recursive law: the same two-group identity can be used repeatedly without changing the total.

It resembles the decomposition of a quadratic physical energy into an overall contribution and contributions from internal differences. No particular branching ratio is selected by the identity.

### The same four cells, examined in two different pairings

Use the four-cell arrangement from Chapter 21: every reference is 100 J, every \(K\) is \(1/(100\ {\rm J})\), and the amounts are

\[
(x_A,x_B,x_C,x_D)=(140,100,100,60)\ {\rm J}.
\]

The total reference and total amount are both 400 J. There is no total shortage or excess. Nevertheless the total field is 16 J: A contributes 8 J and D contributes 8 J.

First look at the pairs \(\{A,B\}\) and \(\{C,D\}\). The left pair has 240 J against a 200 J reference, so its ratio is 1.2. The right pair has 160 J against a 200 J reference, so its ratio is 0.8.

The hierarchy separates the same 16 J as follows:

| Difference being described | Field term |
|---|---:|
| Whole collection against its total reference | 0 J |
| Left pair's ratio 1.2 against right pair's ratio 0.8 | 8 J |
| A's ratio 1.4 against B's ratio 1.0 | 4 J |
| C's ratio 1.0 against D's ratio 0.6 | 4 J |
| Total | 16 J |

For example, the left-versus-right term is

\[
\frac{(200\ {\rm J})(200\ {\rm J})}{2(400\ {\rm J})}
(1.2-0.8)^2=8\ {\rm J}.
\]

Now look at the different pairs \(\{A,D\}\) and \(\{B,C\}\). Each pair contains exactly its 200 J reference, so there is no difference between the pair ratios. But A and D are still different from each other. Their internal term is

\[
\frac{(100\ {\rm J})(100\ {\rm J})}{2(200\ {\rm J})}
(1.4-0.6)^2=16\ {\rm J}.
\]

B and C contribute no internal difference. The complete total is again 16 J.

Nothing moved between these two descriptions. We changed which pairs we examined, not the physical amounts. The calculation cannot earn EBU by itself.

If an actor actually moves 40 J from A to D, all four amounts become 100 J. Now every term becomes zero, and that actual change has the positive complete contribution \(16\ {\rm J}/W_{\mathrm{Cs}}\).

This is why an average alone is insufficient. The pair \(\{A,D\}\) already had the right total before the transfer, but its two members did not individually have their reference amounts.

Appendix C shows the two-group calculation from which the entire hierarchy follows.

## 31. Division is not growth

We must now separate two changes that can both increase the number of cells.

### More pieces of the same system

Divide C into a thousand proportional pieces.

The total reference, total resource, and total field are unchanged.

The number of pieces rises. The modeled amount of cell does not.

### More actual system

Add a second genuine copy of C.

If the copy has the same relative condition, the total reference, resource, and field all double.

This is growth, not division.

For \(n\) identical copies:

\[
X^*=n x_C^*,\qquad
X=n x_C,\qquad
\Phi_{\rm total}=n\Phi_C.
\]

The slope of each copy remains \(m_C\).

The equivalent equalized aggregate response is

\[
K_{\rm aggregate}=\frac{K_C}{n}.
\]

### Which quantities stay constant as the system grows?

For homogeneous replication, the following remain unchanged:

\[
\frac{X}{X^*}=y_C,
\qquad
K_{\rm aggregate}X^*=\kappa,
\qquad
\frac{\Phi_{\rm total}}{X^*}
=\frac{\kappa}{2}(y_C-1)^2.
\]

The field per unit of reference stays constant. The total field grows with the total reference.

This is a concrete scale law. It does not require a special sequence of cell numbers.

### What happens to conservation when a new cell is included?

The earlier constant \(\mathcal B\) referred to a specified complete collection.

If we add a new cell with an existing positive field, we have enlarged that collection. Its opening contribution must be represented.

For example, if a new cell enters the accounting boundary with field \(\Phi_{\rm new}\) and no EBU account change, the quantity \(W_{\mathrm{Cs}}G+\Phi_{\rm total}\) rises by \(\Phi_{\rm new}\).

That is not a violation of the closed-system identity. It means the system is no longer the same closed system.

If we later restore the new cell, its field can support the corresponding EBU contribution. But we must not pretend that the new opening field appeared inside the old invariant with no change of boundary or other entry.

This is where a model of real growth is needed. The division law prevents free reward from multiplying pieces; it does not by itself decide which newly established cells should enter the economy.

## 32. What does “infinitely many cells” mean?

There are at least two very different possibilities.

### Infinitely many pieces of a finite total

Take fractions

\[
\frac12,\frac14,\frac18,\ldots
\]

of an original cell. Their sum is one.

If each piece inherits the proportional reference, amount, and \(K\), every finite partial collection has the corresponding fraction of the original field. The infinite sum equals the original field.

The number of pieces is infinite, but the total reference, resource, and field remain finite.

This is a meaningful mathematical limit because the sums converge.

### Infinitely many full-sized copies

Now take infinitely many copies each with the original positive reference.

The total reference diverges. If each has the same positive field, the total field also diverges.

There is no finite global total to use in the earlier finite-budget statement.

We can study quantities per unit of reference, or restrict attention to finite regions, but we must say which comparison we mean.

The symbol “infinity” cannot be used as if it were just a very large finite cell count while retaining every finite-total conclusion.

### Why this matters economically

Dividing the same available system more finely does not create unlimited EBU potential.

Expanding the represented system without bound is a different assumption. Whether that expansion corresponds to real resources, real functions, and a consistent opening account is not settled by the cell count.

These distinctions let us study large and even ideal infinite networks without losing conservation through a change in what “the system” contains.

## 33. Can Fibonacci numbers appear?

They can, but we must identify the rule that produces them.

The Fibonacci sequence begins

\[
1,1,2,3,5,8,13,\ldots
\]

Each term is the sum of the previous two:

\[
F_{n+1}=F_n+F_{n-1}.
\]

If we choose a construction in which the reference of the next aggregate is the sum of the previous two references, with equal initial reference units, then the aggregate references follow this sequence.

For same-type cells,

\[
x_n^*=F_n x_0^*,
\qquad
K_n=\frac{\kappa}{F_nx_0^*}.
\]

The ratio of successive large reference amounts approaches the golden ratio

\[
\varphi=\frac{1+\sqrt5}{2}.
\]

But the Fibonacci recurrence was the chosen construction rule. The quadratic field did not force us to choose it.

If we always double the previous aggregate, the sequence is \(1,2,4,8,\ldots\). If we always add one fixed-sized cell, it is \(1,2,3,4,\ldots\).

All these constructions can preserve the same composition laws.

### What would make a Fibonacci result stronger?

A stronger result would derive the recurrence from an independently justified physical arrangement or an optimization problem, rather than choosing it as a pattern.

There is a useful capacitor example where that happens. It also shows precisely what extra structure is required.

## 34. A capacitor ladder that really produces the golden ratio

Consider this specific electrical arrangement.

At each stage there are two routes between the input terminal and the reference terminal:

1. One capacitor of capacitance \(C_e\) connects directly between the terminals.
2. Another capacitor of capacitance \(C_e\) is in series with the rest of the ladder.

The two routes are in parallel.

Let the capacitance of the remaining finite ladder be \(C_e c_n\), where \(c_n\) is a dimensionless ratio.

The series branch has capacitance

\[
\frac{C_e(C_ec_n)}{C_e+C_ec_n}
=C_e\frac{c_n}{1+c_n}.
\]

Adding the parallel capacitor gives

\[
\boxed{
c_{n+1}=1+\frac{c_n}{1+c_n}.
}
\]

This follows from the standard series and parallel capacitor rules, not from fitting a curve to a desired constant. The physical composition rules are given in [MIT's capacitor and circuit summary](https://ocw.mit.edu/courses/8-02-physics-ii-electricity-and-magnetism-spring-2007/0d0fd6cf993958db9fbd7738c21e51e1_summary_w05d1.pdf); the repeated-ladder calculation here applies those rules to the stated arrangement.

Start with one terminating capacitor, so \(c_0=1\). Then

\[
c_1=\frac32,\qquad
c_2=\frac85,\qquad
c_3=\frac{21}{13},\qquad
c_4=\frac{55}{34}.
\]

These are ratios of alternating Fibonacci numbers:

\[
c_n=\frac{F_{2n+2}}{F_{2n+1}}.
\]

### Why the limit is the golden ratio

If the ratio approaches a limit \(c\), the recurrence gives

\[
c=1+\frac{c}{1+c}.
\]

Multiply by \(1+c\):

\[
c+c^2=1+2c.
\]

Therefore

\[
c^2-c-1=0.
\]

The positive solution is

\[
\boxed{c=\varphi=\frac{1+\sqrt5}{2}.}
\]

The limit exists: the recurrence starts at 1, increases while below \(\varphi\), and stays below \(\varphi\). Thus it approaches the fixed point.

### Does our current cell network have this golden ratio?

Not merely because our fields resemble capacitor energy.

The ladder uses two different composition rules:

- parallel capacitances add;
- series capacitances combine by reciprocal addition.

Our independent-cell joining rule supplies the first kind of behavior for the quantity \(1/K\). It does not automatically supply the ladder's series operation, electrical boundary conditions, or two-terminal structure.

Therefore this is a genuine physical example and a useful research clue, not a proved universal EBU ratio.

The clue is specific:

> Repeated arrangements can generate characteristic constants when their physical composition rules produce a recurrence.

We should look for the recurrence justified by our economic-cell operations. We should not select \(\varphi\) first and force the cells to fit it.

### Does the golden ratio determine the best number of cells?

Nothing in the calculation says that.

It describes the limiting equivalent capacitance of one particular ladder. It does not establish maximum EBU gain, minimum geographical distance, optimal division, or survival of a spaceship.

Those would be different claims requiring their own comparisons.

# Part IX. What the laws tell us about incentives

## 35. A catalogue of behaviors, with their reasons

We can now state the behaviors in ordinary language and point to the exact calculation behind each.

### 1. Restore a depleted cell

While \(x<x^*\), adding resource decreases the quadratic field and produces positive EBU.

The next unit earns more when the cell is further below its reference, for a fixed cell specification.

This resembles a capacitor-like response that grows with departure. It is a statement about the value of the next actual change.

### 2. Stop treating every added unit as equally valuable

As restoration proceeds, the positive marginal decreases. At the reference it becomes zero. Beyond the reference, further additions are negative.

This is why a frozen initial quote is not the value of the whole finite action.

### 3. Supply from an overfilled cell

If \(x>x^*\), removing resource brings the cell toward its reference and produces positive EBU.

The model can therefore reward supplying resource from one place and adding it at another in the same operation, when both changes reduce imbalance.

### 4. Accept a temporary negative contribution for a better complete operation

Overfilling A can be part of an operation that later supplies B. The field cost at A can be recovered, while B's actual improvement produces the net gain.

This is an investment interpretation with an exact accounting calculation, not a promised return merely for waiting.

### 5. Move from higher current slope to lower current slope

For a small compatible transfer, the gain is

\[
(m_{\rm donor}-m_{\rm receiver})dq/W_{\mathrm{Cs}}.
\]

This is the direct redistribution signal.

### 6. Equalize relative provision for same-type cells

Under common \(\kappa\), equal slopes mean equal \(x_i/x_i^*\).

Large cells can retain more joules than small cells while being equally supplied in the model.

This is why “spread resources equally” must not be interpreted as identical amounts in every box.

### 7. Repair distribution without pretending to repair total shortage

Redistribution can remove the unevenness term. It cannot change the total-resource term.

The exact separation tells us how much EBU gain is available from rearranging what already exists.

### 8. Share a required withdrawal across available cells

When cells begin equally supplied, a concentrated withdrawal can be more expensive than an appropriately distributed withdrawal.

At the references, the least-cost same-type allocation supplies the same fraction of each reference.

### 9. Divide without being paid simply for division

A proportional split inherits resource, reference, and response together. It preserves field and current marginal.

The incentive for division must come from what the resulting independent parts make possible later, not from multiplying the number of cells.

### 10. Pay for creating unequal conditions

An unequal split adds a definite positive square term to the field.

If repairing that inequality later produces EBU, the earlier opposite change prevents a free closed-cycle gain.

### 11. Join without permanently changing the restored response

References add and reciprocal \(K\) values add. Splitting and correctly rejoining restores the original aggregate \(K\).

No repeated round trip makes the same restored cell artificially cheaper to disturb.

### 12. Cooperate when the complete operation has a positive surplus

One participant may have a negative physical contribution while another has a larger positive contribution.

Transfers of existing EBU can divide the complete gain so both benefit. The total remains the complete field decrease.

### 13. Improve access without pretending a connection is already an improvement

A new allowed route can make useful redistribution reachable.

Opening the possibility and performing the physical improvement are different events. The field contribution belongs to the represented change, not to the number of lines drawn.

### 14. Keep the complete field when describing large groups

An overall average and the differences inside the group together reproduce the complete quadratic field.

Ignoring the internal differences would remove real imbalance from the calculation without removing it from the cells.

### 15. Do not confuse token gain with every kind of physical efficiency

For the same complete endpoint, the signed field contribution is the same. Different routes can nevertheless require different handling.

The least-resource theorem must specify what resource is counted and which actions are allowed.

### 16. Do not expect a rate of response from a price of change

The equations say which permitted next change earns more EBU. They do not say how many people respond tomorrow, or how quickly a cell refills.

That is not the disappearance of the incentive. It is the distinction between valuing an available action and predicting the rate at which it is chosen.

## 36. The physics connections, and what we are borrowing from each

The strongest analogy is not one magical particle. Different parts of the model have different physical counterparts.

| EBU result | Closest useful physical structure | What the comparison does not supply |
|---|---|---|
| Quadratic field and linear slope | Capacitor energy and voltage; a linear spring's potential | The correct reference for a particular economic resource |
| Equal slopes after exchange | Equal voltages; equality of the relevant chemical potentials | Automatic agreement or action by people |
| Larger size means smaller \(K\) for the same relative condition | Larger capacitance gives smaller voltage change for the same charge increment | A universal common material type |
| Field gain from removing an unequal distribution | Decrease of stored energy during equalization | A second EBU reward in addition to the complete field decrease |
| Group-boundary resource balance | Kirchhoff-style conservation | A current or flow-rate law |
| Zero complete value around a closed state cycle | Work from an exact potential difference | Zero physical handling or zero real dissipation along every route |
| Hierarchical decomposition into overall and internal differences | Decomposition of quadratic energies | Permission to erase internal conditions by grouping |
| Better access cannot worsen the best attainable result | Monotonicity ideas in electrical networks | Guaranteed improvement of actual private choices |
| Least-resource result under specified access | Variational and allocation principles | A universal greedy theorem for all topologies |
| Golden ratio of one recursive ladder | Series–parallel capacitor recurrence | A universal preferred EBU branching ratio |

In thermodynamics, equality of chemical potential is an equilibrium condition for the exchange of the corresponding substance under the appropriate constraints. That is a close conceptual relative of equal derivatives in our fixed-total problem. [MIT's lecture on uniformity of chemical potential](https://ocw.mit.edu/courses/3-00-thermodynamics-of-materials-fall-2002/5095456b7171d72056b09ff35a5e4e55_lecture_28_oneside.PDF) provides the physical setting.

We do not need to adopt a logarithmic field to recognize this connection. The common mathematical idea is that the derivative tells us the effect of transferring another unit.

For resistor networks, Thomson's principle minimizes a specified quadratic dissipation among flows satisfying conservation. This gives another example of physics producing a global result from an explicitly defined quantity and constraints. It is not a reason to insert resistance or a time law into our present cells. The relevant physical theorem is described in [Doyle and Snell, section 1.3](https://math.dartmouth.edu/~doyle/docs/walks/walks.pdf).

The practical lesson from these comparisons is consistent: name the physical quantity, name the allowed change, and keep the complete energy-like calculation.

## 37. Which parts determine the field, and which parts do not?

The results are strong enough to constrain a model, but we should be precise about what they select.

### Division consistency selects a size relationship

If a same-type field has the form

\[
\Phi(x;x^*)=x^*\,\psi(x/x^*),
\]

then a proportional split preserves the total field:

\[
\sum_i
\alpha_i x^*\,
\psi\!\left(\frac{\alpha_i x}{\alpha_i x^*}\right)
=x^*\psi(x/x^*).
\]

This works for many functions \(\psi\), not only the quadratic one.

The quadratic choice is

\[
\psi(y)=\frac{\kappa}{2}(y-1)^2.
\]

Thus division consistency supports the extensive size form. The additional assumption of a linear response to relative departure selects the quadratic shape within that form.

### Conservation does not select the shape by itself

Any sufficiently smooth fixed field with actual contributions

\[
dE=-d\Phi/W_{\mathrm{Cs}}
\]

has the complete endpoint identity.

Conservation checks whether we have counted the changes consistently. It does not prove that every chosen \(\Phi\) represents the right economic condition.

### The reference still needs meaning

The cell's reference is not determined merely by observing that redistribution goes from high slope to low slope.

To see why, add the same constant \(c\) to every slope. Every pair difference stays unchanged:

\[
(m_A+c)-(m_B+c)=m_A-m_B.
\]

At fixed total resource, adding \(c\sum_i x_i\) to the total field changes no redistribution value. But it does change the value of bringing resource into the whole collection or removing it.

So internal exchange preferences alone cannot determine the common level against which external additions and removals are judged.

This is a mathematical reason why the reference question remains important. It does not undo the exchange laws; it identifies information those laws do not contain.

For our chosen quadratic cells, fixing \(x_i^*\), \(K_i\), and the zero-field convention supplies that information as part of the model.

### What is the strongest honest description of this book?

We have a coherent ideal quadratic-cell model with exact valuation, composition, redistribution, and conservation results.

We have positive least-resource results under named access and progress assumptions, and an exact counterexample to a broader topology claim.

We have physical analogies that explain several equations and show useful research directions.

We do not yet have a universal physical derivation of every resource reference, a proof of long-run spaceship survival, or a unique field forced by all of nature.

Those are larger claims. The appropriate next step is to use the present laws as non-negotiable checks while giving one economic cell a precise resource meaning and a precise set of permitted actions.

The important difference from starting again is that the next model cannot arbitrarily change size, split value, reference, or accounting without facing these equations.

---

# Part X. Connecting the same cell to a source

## 38. What exactly is the physical connection?

We now keep the cell studied throughout this book and ask how a real source can supply it. Its field remains

\[
\Phi(x)=\frac12K(x-x^*)^2.
\]

The source supplies resource. The cell represents the current provision of that resource and assigns the imbalance value used by EBU. Resource can remain available in the cell after its source stops supplying it. The source need not remain attached for the cell to continue existing.

### An actual delivery, using the same field

Suppose a wind installation supplies usable electrical energy to a cell. Define \(x\) as the usable energy currently available there, measured in joules.

If an identified delivery increases that amount by one kilowatt-hour,

\[
\Delta x=3{,}600{,}000\ {\rm J}.
\]

This is the amount actually added to the represented resource. It is not automatically all the energy generated at the turbine.

When this delivery is the only represented change, the existing field evaluates it:

\[
E=\frac{\Phi(x)-\Phi(x+\Delta x)}{W_{\mathrm{Cs}}}
=-\frac{K(x-x^*)\Delta x+\tfrac12K(\Delta x)^2}
{W_{\mathrm{Cs}}}.
\]

A delivery toward the reference can earn EBU. A delivery farther above it can consume EBU. A large delivery crossing the reference contains both parts, and the equation counts the complete change.

With simultaneous actors, we instead identify each actual contribution against the current field, as in Chapters 17–18. We do not award the entire endpoint difference to each actor.

We have now connected an actual delivery to \(\Delta x\), without replacing the field. We have not yet derived \(K\) or \(x^*\) from wind observations. Those are different questions.

### Three questions hidden inside “physical connection”

**What enters the cell?** Name the resource and define what counts as available. Explain how a measured addition or removal changes \(x\). Usable electrical energy already has a joule measure.

**What fixes the reference?** Explain why the amount \(x^*\) represents balanced provision. In an ideal study we can state it as an assumption. In an application it needs an independent justification. Average source production does not automatically supply this answer: production over an interval and the amount presently available are different quantities.

**What fixes K?** Explain why a given departure produces the stated field response. We may begin with a declared ideal parameter, then seek an independent physical response measurement or a justified statistical estimate.

These are three pieces of information for the same field, not three replacement models.

### When the resource arrives in kilograms

Suppose a fixed-quality resource has a declared usable-energy conversion \(\epsilon\), in joules per kilogram. For its represented mass \(M\),

\[
x=\epsilon M,\qquad dx=\epsilon\,dM,
\]

so

\[
dE=-\frac{K(x-x^*)\epsilon\,dM}{W_{\mathrm{Cs}}}.
\]

The conversion states precisely which quantity this cell represents. It does not make different materials interchangeable merely because their energy contents match.

If quality changes and \(\epsilon\) changes, the complete differential becomes \(dx=\epsilon\,dM+M\,d\epsilon\). That extra change would need to be represented. Keeping the conversion fixed is a legitimate simplifying assumption for the present ideal model.

### Does the source continually rewrite the cell?

No. In our independent-cell model, if the source disappears while \(x\), \(x^*\), and \(K\) remain unchanged, the cell's field remains unchanged.

An actual delivery changes \(x\). The same equation then evaluates the new condition. A decision to revise \(K\) or \(x^*\) is a different represented operation, governed by the changing-parameter discussion in Chapter 15. It cannot be silently included in an ordinary delivery.

### Why ask about energy change when the delivery is already in joules?

Two different quantities are measured in joules:

\[
\Delta x=\text{change in represented resource},
\qquad
\Delta\Phi=\text{change in imbalance}.
\]

In our continuing example, adding 20 J to A when A contains 20 J lowers its field by 14 J. The delivery is 20 J; the field improvement is 14 J; the contribution is \(14\ {\rm J}/W_{\mathrm{Cs}}\).

The question is therefore not “how many joules were delivered?” again. It is “how much does that delivery improve or worsen the condition we are valuing?”

Source production effort is another quantity. The model does not automatically equate production effort, delivered resource, and field improvement.

### A precise recipe for the next application

1. Name one resource and define the cell's amount \(x\).
2. Explain how an actual delivery changes \(x\), with units.
3. Give \(x^*\) an explicit meaning, initially as an assumption if necessary.
4. Specify \(K\), initially as an assumed ideal response if necessary.
5. Evaluate identified changes using our unchanged field.
6. Check size scaling, split–merge composition, current-field addition, and complete conservation.
7. When replacing an assumed parameter with an estimate, establish why the observation measures that parameter.

The first six steps define a conditional application. The seventh strengthens its physical interpretation. We need not redesign the cell to perform it.

## 39. Can a Gaussian bell help determine K?

Yes, if we establish a particular relationship between the observations and this cell's energy-valued field.

The field itself is a bowl, lowest at \(x^*\). A probability bell is highest near its centre. They describe different things: the size of imbalance and the frequency of observed conditions.

### Why this matters for the cell we designed

In the introduction we specified K as the strength of the response. This chapter asks whether observations can tell us that strength independently, instead of leaving it as an assumed parameter. It does not turn the source into the cell or require the cell to follow the source's current output.

Under the statistical relation below, compare two cells observed at the same independently justified energy scale Θ. If the second has twice the standard deviation σ, its variance is four times as large and its inferred K is one quarter as large. For the same departure from their respective references, its field is then one quarter as large. This is how a measured spread could affect an EBU valuation, once the physical and statistical premises hold. It is not a rule that a more variable source must always receive a weaker K.

We keep two questions separate: what response the economic-cell design requires, and whether a physical system's observations support that response. A Gaussian fit can assist the second question; it does not choose a desirable reference or prove that the economy will remain viable.

### The mathematical connection

Suppose a justified statistical description of this same coordinate is

\[
p(x)=\frac1Z\exp[-\Phi(x)/\Theta],
\]

where \(p(x)\) is probability density, \(Z\) makes its integral one, and \(\Theta>0\) is an independently known energy scale in joules. The exponent is dimensionless.

Substitute the existing quadratic field:

\[
p(x)=\frac1Z
\exp\!\left[-\frac{K(x-x^*)^2}{2\Theta}\right].
\]

For a full, untruncated Gaussian, the exponent is \(-(x-x^*)^2/(2\sigma^2)\), where \(\sigma^2\) is variance. Comparing them gives

\[
\boxed{\sigma^2=\Theta/K,\qquad K=\Theta/\sigma^2.}
\]

Because \(x\) is in joules, its variance is in squared joules. The result for \(K\) is in inverse joules, as required.

Thermal equilibrium supplies a real example: the canonical distribution uses the scale \(k_{\rm B}T\) with the appropriate physical energy and state measure. A harmonic coordinate then has Gaussian fluctuations. See [MIT's canonical-ensemble lecture, classical harmonic oscillator on page 10](https://live.ocw.mit.edu/courses/8-044-statistical-physics-i-spring-2013/8060bdb2909016322cc323d867682179_MIT8_044S13_L13.pdf). This supports the physical example; it does not establish that wind production follows the same description.

### What does “establish the connection” require here?

First, the observations must concern the same \(x\). Wind speed, delivered power, daily production, and currently available resource are not automatically the same coordinate.

Second, there must be a reason for the stated probability law. An economic cell's observations can reflect weather, choices, imposed limits, and demand. A bell-shaped histogram alone does not establish that its spread was produced by the response \(K\).

Third, the energy scale \(\Theta\) must be known independently. Otherwise only \(K/\Theta\) is identified.

There is a short proof of this last limitation. Replace \(K\) by \(aK\) and \(\Theta\) by \(a\Theta\), for any \(a>0\). The probability distribution is unchanged, but the energy-valued field and its EBU consequences are multiplied by \(a\).

Thus the same bell can describe different EBU scales. The missing information is specific: the physical relationship and its energy scale.

### Our cesium ruler does not change

\[
K=\Theta/\sigma^2
\quad\text{would estimate the response,}
\]

\[
E=-\Delta\Phi/W_{\mathrm{Cs}}
\quad\text{expresses the contribution in EBU.}
\]

We do not replace \(W_{\mathrm{Cs}}\) with variance, temperature, noise, or a resource-specific denomination.

### Changing units does not change the field

If an observed coordinate \(q\) becomes \(x=a q\) through a fixed conversion, its variance changes according to

\[
\sigma_x^2=a^2\sigma_q^2,\qquad
K_x=\frac{\Theta}{a^2\sigma_q^2}.
\]

This preserves the represented field. A nonlinear conversion needs additional care because the probability density and its shape also change.

### Limits and measurement affect inference

A strictly nonnegative or bounded resource amount cannot have an exact full Gaussian distribution everywhere: the Gaussian assigns some probability outside those limits.

When a boundary cuts off observations, their variance is generally not \(\Theta/K\). We need a distribution respecting that boundary, or an explicitly approximate Gaussian description away from it. This changes how we infer \(K\), not necessarily our quadratic field.

Measurement noise must also be distinguished from actual cell variation. Likewise, the observed mean is not automatically a desirable reference merely because it is the centre of a fitted bell.

### The estimate must respect division

Our same-type rule remains

\[
K_i x_i^*=\kappa.
\]

For a proportional piece with fraction \(\alpha\), \(K_{\rm part}=K/\alpha\). We cannot fit arbitrary unrelated responses to proportional pieces and still claim the original division theorem.

An instructive check is possible. If the piece is described by \(x_{\rm part}=\alpha x\) in every observation, its variance is \(\alpha^2\sigma^2\). It is not an independently fluctuating system automatically sharing the original \(\Theta\). In fact,

\[
K_{\rm part}\sigma_{\rm part}^2
=\frac K\alpha\,\alpha^2\sigma^2
=\alpha\Theta.
\]

Proportionally dividing the same observations is different from measuring independently operating physical pieces. Keeping that distinction prevents a statistical estimate from silently violating the cell's size law.

### A direct response measurement is another possibility

If a physical interpretation independently identifies our marginal \(m\), two measurements in the quadratic regime give

\[
K=\frac{m(x_2)-m(x_1)}{x_2-x_1},
\qquad
x^*=x_1-\frac{m(x_1)}K.
\]

The response must have the same energy-change-per-resource-change meaning as our field. Computing \(m\) from an assumed \(K\) and then using it to recover \(K\) would be circular; an independent physical measurement supplies information that calculation does not.

### What we have clarified

An identified delivery connects the source to the cell's \(x\). A justified observation-to-response relationship can additionally help determine \(K\). Neither operation requires abandoning the quadratic field.

We can first study the cell with explicit assumed parameters and its exact conditional laws. We can then strengthen one particular application by explaining its resource, reference, and physical response. Gaussian observations are one possible aid in that second task, not a new compulsory foundation.

### Companion study: when the edges carry EBU

The owner's separate graph question is developed in [EBU between economic cells: payment graphs and topology](EBU_BETWEEN_ECONOMIC_CELLS.md). It contains proofs and simple diagrams for existing-token payments, funding, strong topologies, and payment access after division. Its payment edges must not be confused with this book's earlier physical resource-transfer routes.

---

# Part XI. EBU Kirchhoff-like laws

## 40. Balance at a participant, balance around a loop

Imagine Anna receives 10 existing EBU from Bob and sends 7 existing EBU to Clara. Anna has 3 more EBU than before. No cell has necessarily changed. Now imagine an actor moves resource from cell A to cell B. Both cell amounts change, and their field changes determine a signed EBU contribution. These are two different events, so we need to say which one each equation describes.

Electrical circuit theory has two famous rules called Kirchhoff's rules: a balance of charge at a junction and a balance of voltage differences around a loop. Their usual circuit forms rely on stated approximations, including negligible charge accumulation at a junction and an appropriate description of the circuit's fields. [Feynman explains both rules and their assumptions](https://www.feynmanlectures.caltech.edu/II_22.html#Ch22-S3).

Our counterparts below follow from the cell and account rules already used in this book. They are laws of this specified model, not claims that tokens are electrical charges or that independent cells have acquired wires. We retain the book's after-action accounting ideal: actual contributions are accumulated against the current field and their exact account amounts are posted once. This does not rewrite the historical acceptance convention discussed earlier.

### First law: every participant's balance change must be explained

For any completed sequence of account operations,

\[
\boxed{
\text{balance change}
=\text{existing EBU received}
-\text{existing EBU sent}
+\text{signed EBU contribution}.
}
\]

All four quantities are in EBU units. The signed contribution is positive when the participant earns EBU through an identified qualified resource contribution and negative when their contribution costs EBU. A transfer received from another participant is not another resource contribution.

In Anna's example the equation is 3=10-7+0. If she also makes a completed contribution worth 2 EBU, her balance change is 5=10-7+2. If instead the resource action costs 2 EBU, the change is 1=10-7-2. These equations explain changes, not whether a particular order of payments is fundable. Anna must still have the required available units when a debit is made under the funded-account assumptions.

For someone who merely passes tokens onward, with no contribution and no balance change, this becomes

\[
\boxed{\text{EBU entering}=\text{EBU leaving}.}
\]

Keeping the balance-change term is important. We do not demand that a participant immediately sends out everything received.

The same law applies to a group. Add the equations of all its members. A payment from Anna to Bob within that group appears once as outgoing and once as incoming, so it cancels. The group's balance change equals payments received from outside, minus payments sent outside, plus the group's signed contributions. This is the proof; it works for two participants or a million. It assumes the specified operations include every change to the balances and introduces no issuance against an unpaid financial promise.

### Second law: current slope differences cancel around every resource loop

Return to cells A, B and C. For each cell,

\[
\Phi_i=\frac12K_i(x_i-x_i^*)^2,
\qquad m_i=K_i(x_i-x_i^*).
\]

The resource amount \(x_i\) and reference \(x_i^*\) are in joules, \(K_i\) is in inverse joules, and the slope \(m_i\) is dimensionless. It describes the field change per next small joule added to the cell. It is not an account balance.

For an identified transfer of a compatible resource amount dq from A to B, dx_A=-dq and dx_B=dq. Therefore

\[
d\Phi_A+d\Phi_B=(-m_A+m_B)\,dq.
\]

The complete signed EBU contribution is consequently

\[
\boxed{dE_{A\to B}=\frac{(m_A-m_B)\,dq}{W_{\mathrm{Cs}}}.}
\]

Here E retains the book's meaning of EBU units, while the numerator is in joules. The equation evaluates this specified resource change, not a token payment. It also does not award the whole amount to each participant: identified contributions must be assigned once.

Now evaluate the possible directions A→B, B→C and C→A at the same current state. Their slope differences add to

\[
\begin{aligned}
&(m_A-m_B)+(m_B-m_C)+(m_C-m_A)\\
&=0.
\end{aligned}
\]

Thus our second law is

\[
\boxed{\text{Current slope differences around a closed resource loop sum to zero.}}
\]

The proof is cancellation: each cell's slope appears once with a plus sign and once with a minus sign. It holds for any number of cells on a loop. Each possible transfer must use a consistent compatible resource coordinate. Different materials cannot be treated as interchangeable merely because their amounts are expressed in joules.

For a concrete current-state example, take m_A=3, m_B=1 and m_C=-2:

| Possible resource direction | Current slope difference |
|---|---:|
| A → B | 3-1=2 |
| B → C | 1-(-2)=3 |
| C → A | -2-3=-5 |

The sum is 2+3-5=0. Multiplying a row by a specified infinitesimal resource amount and dividing by the cesium ruler gives its EBU contribution. For unequal amounts on the three connections, the total contribution need not vanish: the cells' amounts then need not remain unchanged. The zero sum of bare slope differences is a loop identity, not permission to discard the amounts from contribution calculations.

### A consequence: not every direction around a loop can offer positive gain

Suppose all three directions in a closed loop had strictly positive current slope differences. Their sum would then be positive. But the second law says that the sum is zero. This contradiction proves:

> At a fixed current state, there is no closed loop of resource-transfer directions all offering strictly positive complete marginal contributions.

Equivalently, following a strictly positive direction always takes us from a higher slope to a lower slope. A finite chain of strict decreases cannot return to its starting slope.

This is a useful consistency check for future calculations. A claimed all-positive loop may indicate that different states were compared, an actual change was omitted, or a contribution was counted twice. It does not establish that every actor's private payment will have the same sign as the complete contribution. Agreements can redistribute existing EBU.

Nor does this prohibit tokens from circulating around a payment loop. Token circulation is a different operation: it can occur with every cell's field unchanged.

### Third law: a complete return to the starting condition gives zero net EBU

The previous loop identity concerns one current state. During a finite resource action the slopes change. We must use those changing slopes, not multiply the initial quote by the whole amount.

Write \(\Phi_{\rm total}\) for the sum of all cell fields. Adding every identified contribution once along a complete operation gives

\[
E_{\rm complete}
=-\frac1{W_{\mathrm{Cs}}}\int d\Phi_{\rm total}
=\frac{\Phi_{\rm total,start}-\Phi_{\rm total,finish}}{W_{\mathrm{Cs}}}.
\]

If the complete condition returns to its start, the field difference is zero:

\[
\boxed{E_{\rm complete}=0\quad\text{for a closed complete sequence}.}
\]

Someone may earn EBU during one part. Another part pays the matching signed amount when the complete starting condition is restored. This concerns the total across all participants, not a promise that every individual finishes with their initial balance.

The word complete matters. Cell references, K values and any relevant external changes must be included; restoring resource amounts while silently changing a reference is not necessarily restoring the state. Permitted splits and merges are included through the rules in Chapters 12–15 and Appendix D. Neutral splits preserve the field. Unequal splits or other non-neutral operations cannot omit their field change and then count a later improvement as free gain.

For the closed collection of accounts, with no uncounted external payments or field contributions, the first law and this field identity give

\[
\boxed{W_{\mathrm{Cs}}G+\Phi_{\rm total}=\text{constant}.}
\]

This is the same conservation law as Chapter 18, now connected explicitly to participant balances and resource loops. It is not a newly imposed equation.

### The capacitor correspondence, without confusing tokens and resource

The capacitor formulas \(U=Q^2/(2C_e)\) and \(V_e=Q/C_e\) match the form of our quadratic field and slope. [Feynman's electrostatic-energy chapter](https://www.feynmanlectures.caltech.edu/II_08.html) supplies the physical comparison.

| Electrical quantity | Corresponding role in our cell equations |
|---|---|
| Charge \(Q\) | Resource departure \(x-x^*\) |
| Voltage \(V_e\) | Field slope \(m\) |
| Capacitance \(C_e\) | Reciprocal response \(1/K\) |
| Electrical energy \(U\) | Imbalance field \(\Phi\) |

This table compares mathematical roles, not equal units. In particular, 1/K is in joules here, not farads, and the dimensionless slope is not a voltage measured in volts. Tokens are not the charge Q in this correspondence. They express the signed contributions in cesium-based units and can subsequently circulate between participants.

The token-balance analogy uses conservation at participants. The capacitor analogy uses resource departure and field slope. Keeping those two mappings explicit lets us use both without pretending that every token payment physically moves resource between cells.

### What these laws establish about topology and best paths

A line, ring, tree or densely connected arrangement must obey the same laws. Adding payment connections does not create EBU. Adding a resource-transfer loop does not create a permanently positive loop of marginal contributions. Adding access can nevertheless make a beneficial resource operation possible where it was previously inaccessible, as Chapter 23 explains.

The laws do not by themselves choose a route or a speed. Even if two routes produce the same complete EBU contribution, one may involve more resource handling, as Chapters 24–28 show. A least-resource claim still needs its declared resource meter and permitted operations. The loop identities neither prove a universal Fermat-like optimum nor select a golden-ratio arrangement.

Our practical checklist is now short: does every token balance change have an explanation; do all loop differences use the same current state; are resource amounts included in contributions; and does every complete closed sequence give zero net EBU? These are exact tests of the model's internal consistency. They leave the actor free to choose among permitted, fundable actions.

---

# Appendices

The chapters above explain the results in ordinary language. The appendices retain the proof details so that the book can also support further mathematical work.

## Appendix A. Proof of the all-pair continuously adjusting exchange result

Keep fixed quadratic fields and write the initial condition as \(x^0\). A proposed endpoint has change

\[
d_i=x_i-x_i^0.
\]

Resource conservation requires \(\sum_i d_i=0\).

If the total amount transferred is at most \(P\), then

\[
\frac12\sum_i|d_i|\le P.
\]

The factor \(1/2\) appears because each directly transferred unit appears once as a donor's decrease and once as a receiver's increase.

Let \(\widehat x\) be the endpoint constructed by lowering high initial slopes to \(u\) and raising low initial slopes to \(\ell\), as in Chapter 26. Assume \(u\ge\ell\), the chosen amounts are physically allowed, and they use exactly \(P\).

Define

\[
a=\frac{u+\ell}{2},
\qquad
b=\frac{u-\ell}{2}\ge0.
\]

Every final slope \(\widehat m_i\) lies between \(a-b\) and \(a+b\).

For any competing change \(d\),

\[
\sum_i\widehat m_i d_i
\ge a\sum_i d_i-b\sum_i|d_i|
\ge-2bP.
\]

For the constructed change \(\widehat d=\widehat x-x^0\), equality holds:

- donor changes are negative and their final slopes are \(a+b\);
- receiver changes are positive and their final slopes are \(a-b\);
- unchanged cells contribute zero.

Therefore

\[
\sum_i\widehat m_i(d_i-\widehat d_i)\ge0.
\]

The exact quadratic expansion around \(\widehat x\) is

\[
\Phi(x^0+d)
=\Phi(\widehat x)
+\sum_i\widehat m_i(d_i-\widehat d_i)
+\frac12\sum_iK_i(d_i-\widehat d_i)^2.
\]

Both extra terms are nonnegative. Hence

\[
\Phi(x^0+d)\ge\Phi(\widehat x).
\]

Since every \(K_i>0\), equality requires the same endpoint.

As \(P\) increases toward equalization, \(u\) decreases and \(\ell\) increases. The constructed endpoints are nested: donors need not take back earlier donations, and receivers need not send back earlier receipts.

Thus one continuously adjusted highest-slope-to-lowest-slope path attains these optimal endpoints.

This proves both the endpoint optimum for each budget and the existence of a path realizing them without extra handling. Both parts are needed for a least-resource statement.

## Appendix B. Exact five-cell counterexample for restricted access

Use \(E_0=1\ {\rm J}\) to keep the calculation dimensionally explicit. Let each cell have

\[
x_i^*=10E_0,\qquad K_i=1/E_0.
\]

Initial amounts are

\[
x^0=E_0(10,14,9,12,14).
\]

Only the four neighboring connections are permitted.

Let \(q=(q_1,q_2,q_3,q_4)\) denote net connection movements measured in units of \(E_0\), positive left to right. Thus the dimensional resource changes are

\[
E_0(-q_1,\ q_1-q_2,\ q_2-q_3,\ q_3-q_4,\ q_4).
\]

The field decrease divided by \(E_0\) is

\[
R(q)=g^{\mathsf T}q-\frac12q^{\mathsf T}Hq,
\]

where

\[
g=(-4,5,-3,-2),
\qquad
H=
\begin{pmatrix}
2&-1&0&0\\
-1&2&-1&0\\
0&-1&2&-1\\
0&0&-1&2
\end{pmatrix}.
\]

The matrix is positive definite: \(q^{\mathsf T}Hq\) is the sum of squares of the five displayed resource-change coefficients, and all five can vanish only when \(q=0\).

For a path with gross handling at most \(PE_0\),

\[
\sum_e|q_e|\le P.
\]

This follows because reversals cannot reduce the handling already performed.

### Optimal endpoint at budget three

Choose

\[
q^{(3)}=
\left(-\frac57,\frac{17}{14},-\frac12,-\frac47\right).
\]

Its absolute entries sum to 3, and direct multiplication gives

\[
g-Hq^{(3)}
=\frac{19}{14}(-1,1,-1,-1).
\]

The signs are exactly the signs of \(q^{(3)}\).

For any \(z\) with \(\sum_e|z_e|\le3\), the exact expansion is

\[
R(z)=R(q^{(3)})
+(g-Hq^{(3)})^{\mathsf T}(z-q^{(3)})
-\frac12(z-q^{(3)})^{\mathsf T}H(z-q^{(3)}).
\]

The middle term is nonpositive because the signed sum of \(z\) cannot exceed its absolute sum, which is at most 3. The last term is strictly negative unless \(z=q^{(3)}\).

Therefore \(q^{(3)}\) is the unique best endpoint for budget three.

Its resource amounts are

\[
E_0\left(
\frac{75}{7},\frac{169}{14},\frac{75}{7},
\frac{169}{14},\frac{94}{7}
\right).
\]

All are positive.

### Optimal endpoint at budget four

Choose

\[
q^{(4)}=(-1,1,-1,-1).
\]

Its absolute entries sum to 4, and

\[
g-Hq^{(4)}=(-1,1,-1,-1).
\]

The same argument proves that it is the unique best endpoint for budget four.

Its resource amounts are

\[
E_0(11,12,11,12,13).
\]

The field has fallen from \(18.5E_0\) to \(9.5E_0\).

Each optimal endpoint can individually be reached with exactly its stated handling: move along the straight interpolation \(q(s)=s q^{(P)}\), \(0\le s\le1\), without reversing a connection. The resource amounts remain positive because they interpolate between positive endpoints.

### Why one path cannot attain both

The net movement difference is

\[
q^{(4)}-q^{(3)}
=\frac1{14}(-4,-3,-7,-6).
\]

Its absolute sum is

\[
\frac{4+3+7+6}{14}=\frac{10}{7}>1.
\]

Any path from the budget-three optimum to the budget-four optimum therefore requires more than one additional unit of handling.

A path that has already used three units has only one unit left at total budget four. It cannot attain both optimal endpoints.

This proves the stated impossibility without assuming a particular choice of greedy tie-breaking, without preventing continuous adjustment, and without adding an interaction term to the cell fields.

## Appendix C. The hierarchy identity

For two groups with positive references \(a=x_L^*\) and \(b=x_R^*\), define

\[
y=\frac{ay_L+by_R}{a+b}.
\]

Direct expansion gives

\[
a(y_L-1)^2+b(y_R-1)^2
=(a+b)(y-1)^2
+\frac{ab}{a+b}(y_L-y_R)^2.
\]

Multiply by \(\kappa/2\).

The first term is the field associated with the group's overall ratio. The second is the difference between the subgroup ratios.

If a subgroup itself contains several cells, apply the same identity inside it. Repeat until the individual cells are reached.

Every application is an equality. Consequently the full hierarchy equals the original sum of cell fields, regardless of the grouping order.

This is also why retaining only an aggregate loses information: it discards explicitly nonnegative difference terms.

## Appendix D. Closed-cycle proof including division and joining

Let \(S_0,S_1,\ldots,S_n\) denote complete modeled conditions. A condition includes the resource amounts, references, response factors, and any internal differences needed for the stated field.

For each permitted operation, take its complete signed contribution to be

\[
E_j=\frac{\Phi(S_j)-\Phi(S_{j+1})}{W_{\mathrm{Cs}}}.
\]

Then

\[
\sum_{j=0}^{n-1}E_j
=\frac{\Phi(S_0)-\Phi(S_n)}{W_{\mathrm{Cs}}}.
\]

All intermediate terms cancel.

If \(S_n=S_0\), the sum is zero.

This includes splits and merges only when their complete field changes are represented. The proportional split has zero change by its algebra. An unequal split has the positive field term derived in Chapter 13. Actual equalization removes the corresponding term.

Returning only the total resource amount is not necessarily a complete cycle. The references or distribution might still differ. Returning the complete specified condition is the relevant test.

Transfers of existing EBU contribute zero to the total circulating amount and therefore do not alter the proof.

## Appendix E. Frequency units and the fixed energy ruler

The field can be expressed as an energy-equivalent frequency:

\[
\nu_\Phi=\frac{\Phi}{h}.
\]

Since \(h\) has units joule-seconds, \(\nu_\Phi\) has units inverse seconds.

For a complete field decrease,

\[
E=
\frac{\Phi_{\rm before}-\Phi_{\rm after}}
{h\nu_{\mathrm{Cs}}}
=
\boxed{
\frac{\nu_{\Phi,\rm before}-\nu_{\Phi,\rm after}}
{\nu_{\mathrm{Cs}}}.
}
\]

The factor \(h\) cancels in this ratio because both numerator and reference have been expressed using it.

This is a change of units for the same valuation. It does not change the quadratic shape, its division law, or the topology of allowed operations.

It is useful because it keeps the cesium connection explicit without requiring a particular atomic model for every cell.

The same formula can be used locally by replacing the complete decrease with the identified differential contribution.

## Appendix F. Exercises with explanations

### Exercise 1. Same amount, different value

A has \(x^*=100\ {\rm J}\), \(K=1/(100\ {\rm J})\). Compare adding 10 J at \(x=20\ {\rm J}\) with adding 10 J at \(x=80\ {\rm J}\).

**Answer.** The first field decrease is \(32-24.5=7.5\ {\rm J}\). The second is \(2-0.5=1.5\ {\rm J}\). Divide each by \(W_{\mathrm{Cs}}\). The first addition earns five times as much because it repairs a larger departure.

### Exercise 2. A finite change from zero slope

Withdraw 5 J from the same cell starting exactly at reference.

**Answer.** The field rises by \(25/200=0.125\ {\rm J}\). The contribution is negative. A zero starting slope does not give a zero finite cost.

### Exercise 3. Divide into ten equal pieces

Divide a cell with reference 100 J, amount 60 J, and \(K=1/(100\ {\rm J})\) into ten proportional pieces.

**Answer.** Each has reference 10 J, amount 6 J, and \(K=1/(10\ {\rm J})\). Each field is \(16/20=0.8\ {\rm J}\). Ten fields sum to 8 J, the original field. Every slope remains \(-0.4\).

### Exercise 4. Withdraw from one piece or all pieces

Starting from Exercise 3, compare withdrawing 1 J from one piece with withdrawing 0.1 J from each of ten pieces.

**Answer.** One piece moves from 6 to 5 J. Its field rises from 0.8 to 1.25 J, a 0.45 J increase. Proportional withdrawal changes each field from 0.8 to \(4.1^2/20=0.8405\ {\rm J}\), a total increase of 0.405 J. The additional 0.045 J in the concentrated operation is due to the new unevenness.

### Exercise 5. Why not make two opposite moves?

Starting from the proportional ten-piece state, move 1 J from one piece into another and then move it back.

**Answer.** The first move creates a slope difference and raises the field by \(\tfrac12(0.1+0.1)1^2=0.1\ {\rm J}\). Reversal lowers it by the same amount. Net EBU is zero.

### Exercise 6. A larger cell is not always the donor

A has reference 100 J and amount 90 J. B has reference 200 J and amount 40 J. Both have \(\kappa=1\). Which small transfer is beneficial?

**Answer.** \(m_A=-0.1\), \(m_B=-0.8\). A→B is beneficial. The larger cell receives because it is more depleted relative to its reference.

### Exercise 7. A payment does not repair a cell

One actor transfers 20 EBU to another while all resource amounts stay fixed.

**Answer.** Total EBU stays fixed and every field stays fixed. What changes is which actor holds the existing units.

### Exercise 8. Can a route earn more by adding an intermediary?

A sends 10 J to C either directly or through B. B finishes in its starting condition and all other represented conditions match.

**Answer.** The complete signed EBU is the same. The two-connection route handles 20 J across connections, while the direct route handles 10 J. The difference in handling is not automatically a difference in the modeled field.

### Exercise 9. New name or new condition?

Two cells have different slopes. They are given one combined name, but their resource amounts remain separately constrained.

**Answer.** The difference term must remain in the complete field. A new name is not actual equalization.

### Exercise 10. Does a golden ratio prove a best economy?

A recursive capacitor calculation converges to \(\varphi\).

**Answer.** It establishes the equivalent capacitance ratio for the specified arrangement. It does not establish the best number, size, or organization of EBU cells.

## Appendix G. Symbol guide

| Symbol | Meaning | Units |
|---|---|---|
| \(x_i\) | Current represented resource amount in cell \(i\) | J |
| \(x_i^*\) | Reference amount for that cell | J |
| \(K_i\) | Strength of its quadratic response | \(1/{\rm J}\) |
| \(\kappa\) | Common product \(K_i x_i^*\) for the chosen same-type family | Dimensionless |
| \(\Phi_i\) | Cell imbalance field | J |
| \(m_i\) | Current field slope \(K_i(x_i-x_i^*)\); D and R identify donor and receiver in Chapter 7 | Dimensionless |
| \(y_i\) | Fraction \(x_i/x_i^*\) | Dimensionless |
| \(X,X^*\) | Sums of resource amounts and reference amounts | J |
| \(\bar y\) | Combined ratio \(X/X^*\) | Dimensionless |
| \(q,Q,P\) | Specified moved or supplied amounts; exact role stated where used | J; Appendix B explicitly uses ratios to \(E_0\) |
| \(P_{\mathrm{EBU}}\) | Payment of existing EBU between participants | EBU units |
| \(E\) | Signed EBU contribution | EBU units |
| \(W_{\mathrm{Cs}}\) | Fixed cesium energy reference | J per EBU unit |
| \(G\) | Total existing EBU in the modeled accounts | EBU units |
| \(\mathcal B\) | Constant \(W_{\mathrm{Cs}}G+\Phi_{\rm total}\) for the stated closed-account ideal | J |
| \(S_K\) | Sum of reciprocal \(K_i\), used in Chapters 10–11 | J |
| \(S_{\mathrm{move}}\) | Total weighted resource handling, used in Chapter 25 | Depends on declared weights |
| \(h\) | Planck constant | J s |
| \(\nu_\Phi\) | Energy-equivalent frequency \(\Phi/h\) | \(1/{\rm s}\) |
| \(C_e,Q,V_e,U\) in the electrical analogy | Capacitance, charge, voltage, electrical energy | F, C, V, J |
| \(\varphi\) | Golden ratio | Dimensionless |

The subscripts in \(S_K\), \(S_{\mathrm{move}}\), and \(P_{\mathrm{EBU}}\) are part of their names. They keep the response sum, resource handling, and token payment visibly separate.

## Appendix H. Sources, scope, and relation to earlier work

### Physical sources

The following sources support the physical comparisons, not the claim that an economic cell is literally an electrical component:

1. [Feynman Lectures, Volume II, Chapter 8: Electrostatic Energy](https://www.feynmanlectures.caltech.edu/II_08.html), especially the capacitor work and energy relationships.
2. [MIT: the two-capacitor problem](https://web.mit.edu/esfaki/www/8.311_files/2.pdf), for equalization and complete physical energy accounting.
3. [MIT 8.02: capacitors and circuits](https://ocw.mit.edu/courses/8-02-physics-ii-electricity-and-magnetism-spring-2007/0d0fd6cf993958db9fbd7738c21e51e1_summary_w05d1.pdf), for series–parallel composition and circuit balance.
4. [W. Craig Carter, MIT: Uniformity of Chemical Potential at Equilibrium](https://ocw.mit.edu/courses/3-00-thermodynamics-of-materials-fall-2002/5095456b7171d72056b09ff35a5e4e55_lecture_28_oneside.PDF), for the thermodynamic equal-potential comparison.
5. [Doyle and Snell: Random Walks and Electric Networks](https://math.dartmouth.edu/~doyle/docs/walks/walks.pdf), particularly the energy principles and network monotonicity.
6. [MIT 6.854: Minimum-Cost Flow](https://courses.csail.mit.edu/6.854/20/Notes/n09-mincostflow.html), for the distinction between routes, cycles, and an explicitly defined route cost.
7. [Feynman Lectures, Volume I, Chapter 26: Optics—The Principle of Least Time](https://www.feynmanlectures.caltech.edu/I_26.html), for the path-measurement analogy.
8. [MIT 8.044, Lecture 13: Canonical Ensemble](https://live.ocw.mit.edu/courses/8-044-statistical-physics-i-spring-2013/8060bdb2909016322cc323d867682179_MIT8_044S13_L13.pdf), for the qualified quadratic-energy/Gaussian connection in Chapter 39.

9. [Feynman Lectures, Volume II, Chapter 22, section 3: Kirchhoff's rules](https://www.feynmanlectures.caltech.edu/II_22.html#Ch22-S3), for the electrical junction and loop laws, including the assumptions behind their circuit forms. Chapter 40 derives the distinct EBU counterparts from this book's own premises.
10. [NIST: Atomic Spectroscopy, Introduction](https://physics.nist.gov/Pubs/AtSpec/node01.html), for the atomic transition energy relation used in the introductory emission/absorption comparison. The analogy does not establish quantum properties of EBU tokens or select the cell field.

All cell derivations in this book are stated in their own notation. No source is cited as independently proving the complete EBU model.

### Reused results and new work

The quadratic cell, current-field contribution, same-type division rule, equal-slope exchange, and complete conservation identity continue the existing study. They are explained here in one sequence rather than presented as a replacement based on a different field.

The overnight work develops the investment calculation, a connected explanation of many-cell unevenness, explicit distinctions among three kinds of topology, component and hierarchy identities, a shortest-handling comparison, and the exact restricted-graph counterexample. The capacitor-ladder recurrence gives a concrete conditional golden-ratio example.

Some of these results are elementary consequences of the selected field rather than new discoveries in mathematics. Calling them laws of this model means that the stated conclusions follow from its premises. It does not claim priority over capacitor theory, convex optimization, or conservation mathematics.

### Project provenance

The immediate explanatory predecessor is:

[Economic-cell split and merge explanation](../provenance/HISTORICAL_REFERENCES.md#reference-1).

The independent-cell part of the ASTRA3 organization study is relevant:

[Reserve organization, field, and token incentives](../provenance/HISTORICAL_REFERENCES.md#reference-2).

This book does not adopt that report's optional shared-field interactions. Each cell's local field remains independent as requested.

Earlier conditional local-optimality results and their exact audit remain separate:

[Interacting pH reserve and local optimality study](../provenance/HISTORICAL_REFERENCES.md#reference-3);
[independent audit](../provenance/HISTORICAL_REFERENCES.md#reference-4).

That earlier audit is not an audit of this new book or its new topology derivations.

The historical transfer-enabled accounting reconciliation is preserved:

[One-source transferable EBU reconciliation](../provenance/HISTORICAL_REFERENCES.md#reference-5).

No older source, report, or governing definition has been overwritten by this book.

### Review status

This is a written theoretical study with explicit proofs and hand-checked examples. No framework code, simulations, AWS work, or new actor-response dynamics were used. No new independent audit has been commissioned or claimed.

The overnight writing and coordinator review are complete for this edition. The review checked the displayed equations, running examples, composition identities, all-pair path proof and restricted-graph counterexample; mathematical signs, units, and local document links were also checked. This describes the work performed, not independent clearance.

The remaining research questions are explicit: how a real economic cell determines its reference and response; which resource operations and account-funding arrangements are actually permitted; and which conditions beyond this field-and-accounting model would support a long-run resource-protection claim. The book supplies a conditional mathematical foundation for those questions, not a proof that every economic arrangement will work.

The later owner-requested extension adds Chapters 38–39. It explains actual source deliveries, the distinct resource and field changes, and the conditions for Gaussian or response-based parameter inference. Its dimensional, scaling, and division checks were reviewed by the author. It leaves the quadratic field and earlier theorems unchanged and adds no independent clearance.

The subsequent owner-requested Chapter 40 gathers the EBU Kirchhoff-like laws in one explanation. It extends the existing Chapter 22 discussion with participant and group token balances, the current-state no-positive-loop consequence, the finite closed-process proof, and the precise capacitor correspondence. The author checked signs, units, the three-cell arithmetic, accumulation terms, current-state versus finite-sequence distinctions, and consistency with split–merge and path results. It changes neither the quadratic field nor the historical account rules and has not received independent clearance.

The expanded introduction defines the cell, its design inputs, signed token creation/consumption, and the atomic-transition comparison before the detailed chapters. It previews the Gaussian/K relationship, with a further plain-language explanation in Chapter 39. The author checked the 20-to-60 J example, contribution signs, fixed cesium scale, frequency-ratio cancellation, and the distinction between a quadratic field and a probability density. These additions explain the existing model and its conditional physical comparisons; they add no source qualification or independent clearance.
