# EBU Real Limits

A cell can assign a value to an additional request even when the resource cannot be divided finely enough to fulfil it. It can contain enough resource while being unable to deliver that amount during the available period. These two limits lead us to the questions developed here: when does an action still improve the cell, when does division help, and which properties must survive as the system grows?

Symbols retain their meanings from the preceding books. New quantities are defined at their first use.

## Contents

- [Whole resource units](#whole-units)
- [Fixed design and finite capability](#fixed-design)
- [When division enables more useful action](#useful-division)
- [The limits of repeated division](#division-limits)
- [What an extended field could change](#extended-field)
- [Further results for growth and connections](#growth-connections)
- [Many simultaneous and repeated operations](#many-operations)
- [The decisions that remain](#remaining-decisions)

<a id="whole-units"></a>

# Part I — Whole resource units

## 1. One resource unit can be too large to help

Assume a resource cannot be divided below one unit worth \(\varepsilon>0\) joules in the chosen coordinate. Allowed resource amounts might then be \(0,\varepsilon,2\varepsilon,\ldots\). This is a property of the selected resource and operation, not a universal smallest energy or the cesium ruler \(W\).

The issue is simple:

> One whole resource unit can be too large to improve a cell that is already close to its reference.

Suppose the cell is below its reference by \(b=x^*-x>0\), with \(b<\varepsilon\). Adding one unit gives \(x+\varepsilon\). Its signed departure is

\[
(x+\varepsilon)-x^*=\varepsilon-b.
\]

We subtract \(b\) because the first \(b\) joules of the addition cover the shortage. The remaining \(\varepsilon-b\) lie beyond the reference.

~~~text
Before addition             Reference             After one unit
      x ---------------------- x* ------------------ x + epsilon
             distance b             distance epsilon - b
~~~

The field is smaller afterward precisely when the new distance is smaller:

\[
\varepsilon-b<b
\quad\Longleftrightarrow\quad
b>\varepsilon/2.
\]

If the shortage is less than half a unit, adding a whole unit overshoots too far. If the shortage is exactly half a unit, the two endpoints have equal field.

The exact algebra covers both sides of the reference. With \(d=x-x^*\),

\[
\Delta\Phi_{\rm add}=K\varepsilon(d+\varepsilon/2),
\]

\[
\Delta\Phi_{\rm remove}=K\varepsilon(-d+\varepsilon/2).
\]

Addition improves the field when \(d<-\varepsilon/2\). Removal improves it when \(d>\varepsilon/2\), provided removal is physically possible. Neither lowers it when

\[
\boxed{|x-x^*|\le\varepsilon/2.}
\]

This is the half-unit result. It is not \(2\varepsilon\), and it does not declare ordinary paid withdrawals illegal. It only says that neither permitted one-unit change earns a positive contribution from this cell while it is in that interval.

The incentive has changed in a precise way: a small favourable slope is no longer sufficient. The complete unit must improve the endpoint enough to overcome the curvature of the field.

## 2. A reachable reference and the Coulomb-blockade comparison

If allowed amounts are multiples of \(\varepsilon\), and \(x^*=M\varepsilon\) for an allowed integer \(M\), the reference is reachable exactly. Every other allowed amount differs from it by at least one unit. The half-unit interval then contains no allowed amount other than the reference itself.

If \(x^*\) lies between allowed amounts, exact equality may be impossible. The best accessible state is the allowed amount nearest to the reference; two nearest states tie when the reference lies exactly halfway between them.

That is not a failure of the quadratic equation. It reveals a design question: must the desired reference itself be reachable, or may the model intentionally use an ideal reference between accessible states?

This book does not adopt a new rule forcing references onto a resource-unit lattice. It records the issue. Imposing such a rule affects later splits, because each resulting cell would have to satisfy it too. Starting at equilibrium is one possible initial condition, not a derivation of why every future reference remains reachable.

A close physical comparison is single-electron charging. Charge is transferred in electron-sized steps, while the electrostatic preference can be shifted by external gate conditions. The energy required for a complete electron includes a quadratic charging term; the initial voltage alone is not the complete finite-step answer. Under the appropriate low-temperature and junction conditions, some transitions are suppressed because they require additional energy. This is Coulomb blockade. [Graz University of Technology's single-electron derivation](https://lampz.tugraz.at/~hadley/ss2/set/transistor/coulombblockade.php) gives the addition and removal energies explicitly.

The EBU comparison is exact at the level of a quadratic finite difference and an indivisible transferred amount. It does not prove quantum tunnelling in an economy, identify \(\varepsilon\) with electron energy, or block every action with a negative EBU contribution. Actors may perform a paid action for a reason outside the goal of earning EBU from that cell.

The important lesson is that discreteness and a smooth reference can coexist. Physics does not generally force the continuously preferred amount to equal an allowed integer count.

## 3. The final resource unit and an empty cell

Consider a fixed cell with positive reference. At zero resource,

\[
\Phi(0)=\frac12K(x^*)^2.
\]

There is no contradiction in this being positive. It measures how far the represented amount is from its reference. The reference is not energy stored in the empty cell.

To see the accounting issue clearly, start at \(x=x^*\). Suppose resource is removed until \(x=0\). The field rises from zero to \(K(x^*)^2/2\), and the complete signed contribution is negative by that amount divided by \(W\).

Now suppose someone simply removes the cell from the description. If its entire field term disappears, the calculated total falls by exactly the amount just created through depletion. Treating that disappearance as an improvement would refund the depletion without restoring the resource.

The defect would be the disappearance rule, not the conservation proof. The model would have mistaken “we stopped representing this need” for “the need was fulfilled.”

There are legitimate possibilities to investigate. A cell may cease representing a need that truly no longer exists. Its represented condition may be transferred into another cell under a justified merge. Or it may remain empty, with the imbalance still represented. Each possibility has different complete state changes.

Creation must be checked alongside removal. If an arbitrary empty cell can be declared for free and its later filling produces EBU, new reference can manufacture new earning opportunities without a justified new economic condition. Conversely, consistently valuing a creation and its exact reverse makes their algebraic contributions cancel, but algebra alone does not qualify their economic meaning.

This remains an open lifecycle question. No bank, deletion charge or automatic disappearance rule is introduced here.

The capacitor analogy must not confuse us. A conventional uncharged capacitor can have zero electrical energy relative to its chosen zero. An EBU cell with zero resource and a positive reference has nonzero imbalance. These statements concern different state functions and reference choices.

## 4. Why the zero of the field matters when cells appear

For a fixed cell, adding a constant \(a\) to its field changes no resource slope. It may therefore look harmless.

For \(N\) cells, however, adding that constant separately to each gives

\[
\widetilde\Phi_{\rm total}=\Phi_{\rm total}+Na.
\]

A split or removal changes \(N\), so

\[
\boxed{\widetilde E-E
=-\frac{a(N_{\rm after}-N_{\rm before})}{W}.}
\]

A negative per-cell constant rewards increasing the cell count. A positive one penalises it. Neither changes the ordinary resource slope. Therefore slopes alone do not determine fair comparisons between organisations with different numbers of cells.

A single constant added to the complete system cancels between endpoints. A constant added once per newly counted cell does not.

This is why our quadratic convention, its reference terms and the composition rules must travel together. We cannot independently reset the field zero every time a cell is divided and then claim that a new organisational incentive was discovered.

An offset proportional to total reference is also harmless only while that total is unchanged. Growth that admits new reference requires a separate check. Subdivision of an existing reference and admission of new reference are not the same operation.

The general law is straightforward:

> Compare different organisations with one consistent definition of their complete field. Do not generate an incentive by changing the zero used in the comparison.

<a id="fixed-design"></a>

# Part II — Fixed design and finite capability

## 5. What stays fixed while an action happens

Suppose an actor begins supplying resource to cell A. The arrival changes \(x_A\). It must not quietly change \(x_A^*\) to make the action appear better. Nor may the cell lower \(K_A\) halfway through a withdrawal because the original value has become inconvenient.

Our fixed-design rule is:

> During an ordinary resource action, the cell keeps its declared reference, stiffness and capability limits. Split, merge and redesign are separate changes.

When a capacity limit \(B\) or a power limit \(P\) is part of an application, those limits also stay fixed during the ordinary action. The current resource amount is allowed to change; the design used to evaluate the action is not automatically rewritten.

This rule prevents a simple loophole. Without it, someone could change the reference to the current amount before every evaluation. The field would then always be zero, not because imbalance had been removed but because its definition had been moved.

Fixed design has two important limits of meaning. First, it does not mean that only one actor may use a cell. Several identified actions can use the same fixed field. Their contributions follow the established same-current-field rule.

Second, fixed design does not mean fixed total relativistic mass. A physical device that retains additional energy also retains its mass-equivalent. That physical change can occur without rebuilding the device. The equipment design and the total energy of its current state are different things.

If a separate redesign changes parameters, their effects cannot be ignored. For a differentiable change of the quadratic expression,

\[
d\Phi
=K(x-x^*)\,dx
-K(x-x^*)\,dx^*
+\frac12(x-x^*)^2\,dK.
\]

The ordinary-action rule sets \(dx^*=dK=0\). A genuine redesign need not. This equation does not authorise arbitrary redesign; it shows why evaluating only the resource change would be incomplete when the parameters really change.

## 6. How the field amount divides at equal slopes

At the equal-slope condition already established, let the common signed slope be \(m\). Introduce the response scale \(c_i=1/K_i\), measured in joules. Since \(m=K_i(x_i-x_i^*)\), the departure in cell \(i\) is \(c_i m\).

Substitute this into its field:

\[
\Phi_i=\frac12K_i(c_i m)^2
=\frac12c_i m^2.
\]

Therefore, when \(m\ne0\),

\[
\boxed{\frac{\Phi_A}{\Phi_B}
=\frac{c_A}{c_B}
=\frac{K_B}{K_A}.}
\]

This is the additional partition result. At the common slope, a cell with twice the inverse stiffness carries twice the departure and twice the imbalance-field amount. The actual resource amounts can differ because their references can differ.

Equivalently,

\[
\boxed{K_A\Phi_A=K_B\Phi_B=\frac12m^2.}
\]

The common **signed** slope is essential. Opposite slopes can give the same products through the square without being equalised. At \(m=0\), both fields are zero, so their ratio is undefined.

The quantity being partitioned is the energy-valued imbalance field. This formula does not partition every form of physical energy present in the resource.

The new usefulness of \(1/K\) is its role as an additive response scale. Under the established proportional split,

\[
c_A=\alpha c_C,\qquad c_B=(1-\alpha)c_C.
\]

The original scale is shared between the parts. No copy is created. This gives us a quantity against which to test a proposed handling capability in the following chapters.

## 7. Stored amount, capacity and power answer different questions

Return to cell A. Three questions must not be collapsed into one:

1. How much resource does A contain now?
2. How much can its fixed design contain?
3. How much can it deliver during the available period?

For a usable-energy example, write the current amount as \(x\), maximum amount as \(B\), and maximum delivery power as \(P\). Their units are J, J and J/s. Having enough resource answers the first question, not all three.

If no resource arrives during a withdrawal period of length \(T\), then

\[
\boxed{E_{\rm withdrawn}\le x,\qquad
E_{\rm withdrawn}\le PT.}
\]

Thus \(E_{\rm withdrawn}\le\min(x,PT)\). These are necessary conditions. They are sufficient only in a model where the resource is accessible, delivery can use the stated power as required, and no additional restriction prevents it.

For receipts, available space gives \(E_{\rm received}\le B-x\). A receiving-power limit supplies another inequality. Incoming and outgoing powers need not be identical.

Source production is separate again. A slowly regenerating source can accumulate resource and later deliver it quickly. Conversely, a large existing stock can be available through a slow connection. A source's regeneration limit and a cell's delivery limit therefore cannot generally be replaced by one number.

For a positive minimum request size \(\varepsilon\), if each withdrawal is at least that size and no resource arrives, a necessary count bound is

\[
N\le\left\lfloor\frac{\min(x,PT)}{\varepsilon}\right\rfloor.
\]

The floor means the largest integer not exceeding the expression. If each withdrawal is exactly one unit and the ideal conditions above are sufficient, the bound can be attained. Different request sizes or other restrictions can reduce the count.

This does not limit how many abstract price queries can be asked. Nor does it forbid repeated use over an indefinitely long history. It bounds completed resource amounts under the declared stock and period.

The field itself distinguishes none of these powers. Two cells can have identical \(x,x^*,K\) while only one has sufficient delivery capability for a particular task. A complete application needs both valuation and feasible operations.

## 8. What physical laws do—and do not—prove about finite cells

The mass–energy relation for a complete system in its rest frame is

\[
E_{\rm total}=M c_{\rm light}^2.
\]

Retaining additional physical energy changes the system's mass-equivalent. Therefore a fixed finite total mass cannot coexist with an unbounded total rest energy. Einstein's original argument relates an energy change to a mass change of magnitude \(\Delta E/c_{\rm light}^2\). [Einstein, 1905](https://www.fourmilab.ch/etexts/einstein/E_mc2/www/).

However, this does not select a cell's usable operating capacity. It does not tell us what fraction of total rest energy can safely be used, how fast it can be delivered, or what \(x^*\) should be. An application must specify its permitted physical design and conditions.

The distinction matters economically. An expansion is a separate design decision, but not every increase in mass-equivalent is an expansion of the equipment. The ordinary act of retaining energy already changes mass-equivalent. We cannot infer an automatic splitting threshold solely from that change.

There is also a physical restriction on energy flow under a stated premise. For classical matter and fields satisfying the dominant energy condition, local energy flow is causal. Restoring ordinary units gives

\[
|\mathbf S|\le c_{\rm light}u,
\]

where \(u\) is energy per unit volume and \(\mathbf S\) is energy crossing unit area per second. Through a connection of area \(A\),

\[
P\le c_{\rm light}\int_Au\,dA.
\]

Finite area and a bounded permitted density give a finite bound. The energy condition and those bounds are hypotheses, not properties established for every conceivable physical system. [Dain's discussion of the dominant energy condition](https://arxiv.org/pdf/1302.3405) states the underlying causal restriction.

In simple language, more energy stored elsewhere does not necessarily enlarge the opening or change the permitted conditions where delivery occurs. The amount stored can grow while the delivery limit stays unchanged.

This physical example uses an area to explain one mechanism. It does not impose geometric area as an EBU variable. For the economic comparison we may use a justified \(P\), while retaining its physical provenance separately.

Black holes do not provide a fixed-size exception allowing arbitrary energy without other change. In the ideal nonrotating Schwarzschild model, the horizon radius scales with mass. [Dain's Schwarzschild example](https://arxiv.org/pdf/1302.3405#page=16) describes this geometry. It is not a practical economic-cell design law. The useful conclusion here is modest: fixed physical designs have conditions; EBU cannot grant unlimited capability by changing a name.

<a id="useful-division"></a>

# Part III — When division enables more useful action

## 9. A clear handling model, explicitly assumed

Let \(s=x^*>0\) describe size within one declared family of cells. For one specified comparison period and operating conditions, let \(H(s)\) be the greatest resource amount a cell can handle in the chosen direction. It is measured in joules.

Consider the candidate

\[
\boxed{H(s)=\min(\eta s,H_{\max}),\qquad 0<s\le s_{\max}.}
\]

Here \(\eta>0\) is a dimensionless coefficient for that comparison, \(H_{\max}\) is an individual handling ceiling in joules, and \(s_{\max}\) is a maximum permitted reference size.

The meaning is concrete. Small cells have less handling capability. Making a cell larger initially helps, but the individual handling allowance eventually stops increasing. This equation does not follow from the quadratic field; it is an additional capability assumption to investigate for a real application.

Now divide a fixed total reference \(S\) into \(n\) equal cells. Assume their stated allowances can genuinely operate independently, and no common source or connection has a smaller limit. Their complete allowance is

\[
H_n=nH(S/n)=\min(\eta S,nH_{\max}).
\]

This proves a conditional splitting benefit. If the original cell is limited by \(H_{\max}\), several independently usable cells can have a greater total allowance. The benefit stops at \(\eta S\). Division has not created an infinite capability from a finite reference.

For required handling \(E_r\), necessary conditions include

\[
E_r\le\eta S,\qquad
n\ge\left\lceil E_r/H_{\max}\right\rceil,\qquad
n\ge\left\lceil S/s_{\max}\right\rceil.
\]

The ceiling means the smallest integer not below the expression. Within the ideal continuous equal-division model, these conditions ensure the corresponding size and handling bounds. Actual resource availability, indivisible units, funding and shared restrictions still require their own checks.

For any partition, not just equal pieces,

\[
\sum_iH(s_i)\le\eta\sum_i s_i=\eta S.
\]

This is the protection against unlimited handling from unlimited subdivision.

The ratio \(E_r/x\) alone cannot supply this benefit. If both resource and requests divide proportionally, each part has the same ratio as the original. A split helps only if some additional usable capability or access changes. It does not cure a total resource shortage.

## 10. Connecting handling to inverse stiffness

Within a same-type family descended from proportional division,

\[
K_i x_i^*=Kx^*=\kappa.
\]

The product \(\kappa\) is dimensionless and constant for that family. This follows directly from multiplying \(K_i=K/\alpha_i\) by \(x_i^*=\alpha_i x^*\).

Consequently \(s_i=x_i^*=\kappa/K_i\), and the assumed handling model becomes

\[
H(K_i)=\min\!\left(\frac{\eta\kappa}{K_i},H_{\max}\right).
\]

The partition rule now gives a useful complete bound:

\[
\boxed{\sum_iH(K_i)
\le\eta\kappa\sum_i\frac1{K_i}
=\frac{\eta\kappa}{K}
=\eta x^*.}
\]

This is how the energy-partition work helps with handling. It supplies an additive quantity, \(1/K\), against which a proposed capability model can be checked. It does not derive the physical values of \(\eta\) or \(H_{\max}\).

An alternative scaling test makes the missing information especially clear. Suppose, only for comparison, that a part of fraction \(\alpha\) has power

\[
P(\alpha)=P\alpha^\beta,\qquad\beta>0.
\]

For \(n\) equal parts the total is \(Pn^{1-\beta}\). If \(0<\beta<1\), splitting increases that total. If \(\beta=1\), it preserves it. If \(\beta>1\), it reduces it.

All three cases use finite positive powers for finite positive parts. Therefore “every cell has finite power” is not enough to determine the sign of the splitting benefit.

For \(0<\beta<1\), the function \(\alpha^\beta\) is strictly concave. With \(n\) fixed and \(\sum_i\alpha_i=1\), its sum is greatest at equal fractions:

\[
\sum_iP\alpha_i^\beta\le Pn^{1-\beta}.
\]

Thus a common proposed reason for preferring smaller cells can favour equal division rather than a golden split. This is a conditional theorem, not a universal recommendation.

If that power law were extended down to arbitrarily small parts, its total would diverge. A real model would need a minimum size, a shared ceiling or a change of scaling. The capped handling model demonstrates one consistent alternative.

A fixed complete power budget gives a particularly short conservation check. If \(\sum_iP_i\le P_{\rm available}\), then completed amounts in a period \(T\) satisfy

\[
\sum_iq_i\le T\sum_iP_i\le TP_{\rm available}.
\]

Dividing that same budget cannot multiply it. If the original cell could already use it fully for the same requests, subdivision supplies no increase from this fact alone. Whole units can make subdivision less effective:

\[
\sum_i\left\lfloor P_iT/\varepsilon\right\rfloor
\le\left\lfloor T\sum_iP_i/\varepsilon\right\rfloor.
\]

The fractional allowances stranded in separate parts cannot each handle another whole unit. This is another reason that finer division is not always better.

## 11. A proof that splitting can enable more EBU-producing work

Now we can state a genuine incentive theorem without rewarding division itself.

Cell C is below its reference. Let its shortage be \(b=x^*-x>0\). A resource amount \(q\le b\) is available for delivery in a period \(T\). Assume the reference is within capacity, the delivery is otherwise feasible, and the original receiving power is \(P\).

The original cell can receive

\[
a_0=\min(q,PT).
\]

Divide C neutrally into fractions \(\alpha_i\). Specify the resulting fixed powers \(P_i\) from the actual available design; do not copy \(P\) to every part.

Suppose deliveries are proportional to the parts. Receiving a total \(a\) requires \(\alpha_i a\le P_iT\) for every \(i\). The effective power for that proportional delivery is therefore

\[
P_{\rm eff}=\min_i(P_i/\alpha_i),\qquad
a_1=\min(q,TP_{\rm eff}).
\]

A shared source limit would additionally restrict both comparisons.

After a proportional total receipt \(a\), the complete field of the parts equals the field of C after the same receipt:

\[
\sum_i\frac{K}{2\alpha_i}
[\alpha_i(x+a-x^*)]^2
=\frac K2(x+a-x^*)^2.
\]

The contribution from these receiving fields is

\[
E(a)=\frac K W(ba-a^2/2).
\]

For \(0\le a_0<a_1\le b\),

\[
\boxed{E(a_1)-E(a_0)
=\frac{K(a_1-a_0)}W
\left(b-\frac{a_1+a_0}{2}\right)>0.}
\]

Every factor has the stated sign. This proves the claim: **if the split enables more of a restorative delivery, it produces a larger contribution from the receiving cells.**

The initial split contributes zero. The additional EBU corresponds to additional completed improvement.

This is not yet a complete two-sided resource comparison when another represented cell supplies the delivery. That cell's change belongs in the total too. The next chapter includes it explicitly.

For specified positive \(P_i\), proportional delivery uses their full sum when

\[
\alpha_i=P_i/\sum_jP_j.
\]

Indeed, any feasible common power \(p\) satisfies \(\alpha_ip\le P_i\); summing gives \(p\le\sum_iP_i\). The displayed fractions attain equality. If selecting the fractions changes the \(P_i\), however, that dependence must be included before calling this a design optimum.

## 12. The complete split-benefit test

Keep C below its reference by \(b>0\). Let another cell D be above its reference by \(e>0\), with stiffness \(K_D\). D is simply the cell from which the resource is taken.

Move an amount \(a\le\min(b,e)\) from D to C. This reduces both departures. Adding their exact quadratic changes gives the field reduction

\[
R(a)=(Kb+K_De)a-\frac12(K+K_D)a^2.
\]

Here \(R(a)\) is the complete field reduction from this specified transfer, measured in joules.

Its derivative is

\[
R'(a)=K(b-a)+K_D(e-a)\ge0
\]

over the stated range. More completed transfer therefore removes more field from these two cells.

Now compare keeping C whole, allowing transfer \(a_0\), with splitting C and delivering amounts \(q_i\) to its parts. Write \(q=\sum_iq_i\le\min(b,e)\). The split is initially neutral.

The receiving parts end with an extra field, compared with a whole C receiving \(q\), equal to

\[
\frac K2V,\qquad
V=\sum_i\frac{(q_i-\alpha_iq)^2}{\alpha_i}.
\]

This expression has a simple interpretation. It is zero when the delivery proportions fit the division. It is positive when the delivery leaves some parts more disturbed than others.

To derive it, expand

\[
\sum_i\frac{q_i^2}{\alpha_i}
=\sum_i\frac{[\alpha_iq+(q_i-\alpha_iq)]^2}{\alpha_i}.
\]

The first terms sum to \(q^2\); the cross terms vanish because \(\sum_i(q_i-\alpha_iq)=0\). The remaining squares are \(V\).

Let \(D_{\rm other}\) be the final field in other represented properties for the split case minus that for the whole case. It is zero when those properties are unchanged. It is not an invented fee.

The exact complete difference is

\[
\boxed{
W(E_{\rm split}-E_{\rm whole})
=(q-a_0)
\left[Kb+K_De-\frac{K+K_D}{2}(q+a_0)\right]
-\frac K2V-D_{\rm other}.}
\]

Splitting is better precisely when this expression is positive, under the declared feasibility assumptions.

In ordinary language, the additional beneficial transfer must outweigh the extra imbalance left by an unsuitable division and any actual adverse change elsewhere.

If \(q>a_0\), deliveries are proportional and \(D_{\rm other}=0\), the difference is strictly positive. If \(q=a_0\) and other states match, it is \(-KV/2\le0\): the split ties or loses.

The theorem neither assumes that splitting increases power nor denies it. It tells us exactly how a demonstrated capability advantage enters the complete EBU comparison. Individual profit and funding of intermediate actions remain separate from this complete total.

## 13. The best delivery when some parts reach their limits

Fix a permitted split. Let \(h_i\) be the jointly usable receiving allowance of part \(i\), and cap it at the amount needed to reach that part's reference:

\[
b_i=\min(h_i,\alpha_i b).
\]

For a fixed total \(0\le q\le\sum_i b_i\), suppose allowed completed allocations satisfy exactly

\[
0\le q_i\le b_i,\qquad \sum_iq_i=q.
\]

A common source or shared connection may add further restrictions; here we assume those have already been satisfied.

The total taken from D is fixed, so its contribution is fixed. All receiving linear terms are fixed too. Maximising complete EBU is therefore equivalent to minimising

\[
\sum_iq_i^2/\alpha_i.
\]

Choose \(\lambda\ge0\) so that

\[
\sum_i\min(b_i,\alpha_i\lambda)=q.
\]

Then

\[
\boxed{q_i^{\rm best}=\min(b_i,\alpha_i\lambda).}
\]

Such a \(\lambda\) exists because the sum is continuous and nondecreasing from zero to \(\sum_i b_i\). At complete saturation, different values of \(\lambda\) can describe the same allocation.

Give amounts proportionally until a part reaches its allowance; distribute the remainder proportionally among the other parts. This describes the optimal completed amounts, not a queue or a command to actors.

Here is a proof. Call the proposed amounts \(z_i\), and write a competing allocation as \(z_i+\delta_i\), where \(\sum_i\delta_i=0\). The objective difference is

\[
\sum_i\frac{\delta_i^2}{\alpha_i}
+2\sum_i(z_i/\alpha_i-\lambda)\delta_i.
\]

For an uncapped part, the second factor is zero. For a capped part, \(z_i=b_i\), so \(\delta_i\le0\) and \(z_i/\alpha_i-\lambda\le0\). Their product is nonnegative. The squares are nonnegative, and at least one is positive for a different allocation. Thus the proposed allocation is uniquely best.

Whole units have an exact counterpart. If \(q=M\varepsilon\), assign integer counts \(k_i\). The variable term is \(\varepsilon^2\sum_i k_i^2/\alpha_i\). Increasing a count from \(k\) to \(k+1\) adds

\[
\frac{(2k+1)\varepsilon^2}{\alpha_i}.
\]

Each part has an increasing list of these increments. Selecting the \(M\) smallest permitted increments across the lists gives an optimum: whenever a later increment is selected, all its smaller predecessors can be selected first. No competing collection of \(M\) permitted increments has a smaller sum.

This finite calculation is an allocation theorem, not an implementation or prediction. The amount must satisfy \(M\le\sum_i\lfloor b_i/\varepsilon\rfloor\); the continuous condition \(q\le\sum_i b_i\) alone is not enough.

We now possess a real benchmark for a proposed Fibonacci arrangement: compare its feasible completed allocation with this optimum under the same resource amounts and restrictions.

<a id="division-limits"></a>

# Part IV — The limits of repeated division

## 14. How far can a cell containing whole units be divided?

The first stopping condition comes from the resource unit itself.

If total actual resource is \(x=N\varepsilon\) and every nonempty cell must contain at least one whole unit, there can be at most \(N\) nonempty cells. This is just

\[
n\varepsilon\le x.
\]

It does not prove that an empty cell cannot exist; Chapter 3 leaves that question open. It does prove that finite resource cannot supply infinitely many nonempty cells of a fixed positive minimum amount.

If reachable references are additionally required to be integer multiples, simultaneous divisibility becomes stricter. With \(x=N\varepsilon\) and \(x^*=M\varepsilon\), an exactly proportional part requires both \(\alpha N\) and \(\alpha M\) to be integers. For positive \(N,M\), this is equivalent to \(\alpha\) being an integer multiple of \(1/\gcd(N,M)\). If the greatest common divisor is one, there is no nontrivial split satisfying both requirements.

To verify the greatest-common-divisor statement, write \(g=\gcd(N,M)\). There are integers \(u,v\) with \(uN+vM=g\), so integer \(\alpha N,\alpha M\) imply integer \(\alpha g\). Conversely, \(\alpha=k/g\) makes both products integers because \(g\) divides \(N\) and \(M\).

That restriction is conditional on a reference-unit rule we have not adopted. It shows why a seemingly small change in reference design can substantially change the allowed operations.

## 15. Finite resource does not guarantee finite imbalance field

Now let departures shrink at a different rate from the response scales during repeated division.

Give the \(j\)-th cell response scale \(c_j=c\,2^{-j}\), hence \(K_j=2^jK\). Let its positive departure be

\[
d_j=D(1-r)r^{j-1},\qquad D>0,\quad 0<r<1.
\]

The departures sum to \(D\), so the total excess is finite. But the field is

\[
\begin{aligned}
\sum_{j=1}^{\infty}\frac12K_jd_j^2
&=KD^2(1-r)^2
\sum_{j=1}^{\infty}(2r^2)^{j-1}.
\end{aligned}
\]

This geometric series is finite exactly when

\[
\boxed{r<1/\sqrt2.}
\]

Within that range its value is

\[
\Phi_{\rm total}
=\frac{KD^2(1-r)^2}{1-2r^2}.
\]

At \(r=1/2\), departure and response scale shrink proportionally. The result is the equal-slope minimum \(KD^2/2\). Subtracting that minimum gives

\[
\Phi_{\rm total}-\frac12KD^2
=\frac{KD^2(2r-1)^2}{2(1-2r^2)}\ge0.
\]

The numerator explains why only proportional allocation reaches the minimum in this family.

The physical interpretation is not that resource has become infinite. Increasingly small cells become increasingly stiff. If their departures do not shrink fast enough, a finite amount distributed badly can have unbounded total field in the infinite idealisation.

For a fixed indivisible addition \(\varepsilon\), the same point is simpler. Divide a reference-state cell into \(n\) equal pieces. Each has stiffness \(nK\). Adding one whole unit to one piece raises its field by

\[
\frac12nK\varepsilon^2.
\]

The resource unit has not changed. The receiving cell has become smaller and more responsive. This is what “the same unit is a larger disturbance in a smaller cell” means mathematically.

If the physical resource cannot be divided as required to create those pieces, the construction stops before that limit. Infinite equations are consistency tests, not instructions to perform impossible divisions.

## 16. The correct convergence check

Suppose \(c_i>0\), total response scale \(C=\sum_i c_i\) is finite, and the complete field \(\Phi=\frac12\sum_i d_i^2/c_i\) is finite.

Cauchy–Schwarz gives

\[
\sum_i|d_i|
=\sum_i\sqrt{c_i}\frac{|d_i|}{\sqrt{c_i}}
\le\sqrt{2C\Phi}.
\]

The total departure \(D=\sum_i d_i\) is therefore well defined. The many-cell identity remains

\[
\boxed{\Phi
=\frac{D^2}{2C}
+\frac12\sum_i c_i(m_i-D/C)^2.}
\]

It follows by expanding convergent sums, or by first applying the finite identity and controlling the tails. Equality with the minimum requires all slopes to equal \(D/C\), apart from indices of zero weight, which are absent here.

There is a subtler trap. In configuration number \(n\), put a departure \(A2^{-n/2}\) only in cell \(n\), where \(K_n=2^nK\). Every fixed cell eventually has departure zero. The total departure also tends to zero. Yet the complete field is always

\[
\frac12(2^nK)(A2^{-n/2})^2=\frac12KA^2.
\]

Looking at each coordinate separately and declaring the limiting field zero would discard a field amount that never vanished.

For fixed cells, a sufficient measure of closeness between configurations \(a,b\) is

\[
\|a-b\|_c^2
=\sum_i\frac{(d_i^{(a)}-d_i^{(b)})^2}{c_i}.
\]

This measures their difference using the same stiffnesses that define the field. Cauchy–Schwarz proves

\[
|\Phi(a)-\Phi(b)|
\le\frac12\|a-b\|_c(\|a\|_c+\|b\|_c).
\]

Convergence in this measure ensures convergence of the field. The example above does not converge in it.

For growing networks, this gives a practical mathematical warning: checking totals and individual cell amounts is not always sufficient. One must also check the complete field and any remainder omitted from the finite description.

The same discipline applies to complete action sums. Finite closed cycles have zero signed gain. An infinite limiting argument cannot use that fact while silently dropping a nonvanishing tail.

## 17. A limit on handling, not a limit on history

For the capped model from Chapter 9,

\[
H_n=\min(\eta S,nH_{\max})
\longrightarrow\eta S.
\]

After enough equal divisions the sequence is constant. No additional subdivision increases its allowance.

More generally, if a model permits unlimited equal division of a fixed reference \(S\) while claiming finite complete handling, it must satisfy

\[
\sup_n nH(S/n)<\infty.
\]

A sufficient small-size condition is \(H(s)\le Cs\) for a fixed finite \(C\). Then sufficiently small parts obey

\[
\sum_iH(s_i)\le C\sum_i s_i=CS.
\]

Alternatively, a strictly positive minimum design size can terminate refinement. These are different ways of keeping a candidate model finite; neither follows solely from the quadratic field.

We should not turn this into an unrelated ban on repeated transfers. If resource can move back and forth, the same resource can be handled many times. A complete signed EBU cycle can sum to zero while the total amount handled is large.

Only under a separately stated finite gross-handling budget \(Q\), with every event handling at least \(\varepsilon\), does the number of such events obey

\[
N\le\lfloor Q/\varepsilon\rfloor.
\]

Here gross means that adding a unit and later withdrawing it count as two handled units, not zero. The bound is conditional; the theory does not impose a finite lifetime handling budget on every economy.

This distinction is valuable for future studies. A system can be highly active with little net change in field. Field conservation does not measure computational effort, busy equipment or total circulation. Those questions need their own declared quantities rather than being hidden inside \(\Phi\).

<a id="extended-field"></a>

# Part V — What an extended field could change

## 18. Could a different curve reward neutral division?

Consider a general same-type field with positive reference \(s\):

\[
F(x;s)=s f(x/s),
\]

where \(f\) is dimensionless. The quadratic family is included by \(f(z)=\kappa(z-1)^2/2\), with \(\kappa=Ks\).

For a proportional split,

\[
\sum_iF(\alpha_ix;\alpha_is)
=\sum_i\alpha_is f(x/s)
=F(x;s).
\]

This equality does not depend on the shape of \(f\). Replacing the parabola by a different curve in this family cannot reward a subdivision that preserves exactly the same represented condition.

In fact, mild neutrality assumptions force this form. At a fixed resource-to-reference ratio \(z\), write \(g_z(s)=F(zs;s)\). If same-condition joining is neutral,

\[
g_z(a+b)=g_z(a)+g_z(b).
\]

Repeated addition establishes proportionality for integer scales; equal division establishes it for rational scales. Continuity extends it to real scales. Hence \(g_z(s)=s f(z)\), giving the stated formula.

If \(f\) is convex and parts have arbitrary ratios \(z_i=x_i/s_i\), with fixed total resource and reference, convexity gives

\[
\sum_i s_i f(z_i)\ge
S f\!\left(\frac{\sum_i s_i z_i}{S}\right),
\qquad S=\sum_i s_i.
\]

For strict convexity, equality requires equal ratios. Thus the neutral-split result belongs to a broad family of consistent fields; it is not an accident of one quadratic.

There are two possible ways forward. Keep neutral division, and seek useful **later actions** made possible by the arrangement. Or represent an additional real property that changes during physical reorganisation. Calling that changed operation “neutral” would then be misleading.

One can also abandon the old scaling. For example, \(F=A s^p f(x/s)\) makes an \(n\)-part proportional equal split multiply the field by \(n^{1-p}\). For \(p>1\), more subdivision lowers it; for \(p<1\), subdivision raises it. Neither case derives a golden ratio, and both change the old neutrality rule.

The lesson is not that changing the field is forbidden. It is that the changed incentive must have a stated origin and an explicit account of which earlier property it replaces.

## 19. Two conditional physical routes to a real separation incentive

One route changes the shape of \(f\). If it is nonconvex, two different resource-to-reference ratios can have less complete field than one uniform ratio with the same totals:

\[
f(\lambda z_1+(1-\lambda)z_2)
>\lambda f(z_1)+(1-\lambda)f(z_2).
\]

Separating those conditions then reduces the field. Proportional subdivision at the original ratio is still neutral; actual redistribution creates the change.

For small symmetric departures from a uniform ratio \(\bar z\), Taylor expansion gives

\[
\frac S2[f(\bar z+\delta)+f(\bar z-\delta)]-Sf(\bar z)
=\frac S2 f''(\bar z)\delta^2+o(\delta^2).
\]

Negative curvature therefore gives a local incentive to become unequal, under feasible continuous changes. That would sacrifice the quadratic field's general preference for equalisation.

This resembles phase separation. Cahn and Hilliard's physical theory also represents the interface through spatial-gradient terms; those terms cannot be omitted when modelling an actual material. [Their original 1958 paper](https://www.appliedpolymertechnology.org/uploads/1/0/8/8/108867241/cahnhilliard_1958_jchemphys_28_258.pdf) provides the physical comparison.

A second route preserves the quadratic resource response and adds a separately justified organisation field:

\[
\mathcal F=\sum_i\Phi_i+\sum_i h(u_i),
\qquad h(u)=a u^p+b u^q,
\]

with \(a,b>0\), \(p>1\), \(0<q<1\). Here \(u\) is an explicitly new supporting-material amount, for example kilograms; the coefficients have units J/kg\(^{p}\) and J/kg\(^{q}\). This is an exploratory model, not an adopted EBU definition.

The meaning is plain. At fixed total material, the first term falls when material is divided; the second rises. A real separation is favourable when the decrease exceeds the increase.

For total material \(U\), \(n\) equal parts have

\[
\mathcal O_n=aU^p n^{1-p}+bU^q n^{1-q}.
\]

Two equal parts are better than one exactly when

\[
\boxed{
U^{p-q}>
\frac{b(2^{1-q}-1)}{a(1-2^{1-p})}.}
\]

The symbol \(\mathcal O_n\) denotes the organisation-field amount. The proof is subtraction of \(\mathcal O_2\) from \(\mathcal O_1\); both displayed denominator and numerator factors are positive.

A preferred material amount follows by minimising field per kilogram:

\[
\frac{h(u)}u=a u^{p-1}+b u^{q-1}.
\]

Its derivative vanishes once, at

\[
\boxed{u_0=
\left[\frac{b(1-q)}{a(p-1)}\right]^{1/(p-q)}.}
\]

It decreases before that point and increases afterward. Therefore

\[
\sum_i h(u_i)
=\sum_i u_i\frac{h(u_i)}{u_i}
\ge U\frac{h(u_0)}{u_0}.
\]

If \(U/u_0\) is an integer and the parts are feasible, equal parts of size \(u_0\) attain the global minimum among all partitions. Adding another supplied amount \(u_0\) then permits optimal growth without changing any old part. The counts are ordinary consecutive integers, demonstrating that this goal alone does not select Fibonacci.

Charged-drop fission offers a genuine physical comparison: surface energy can oppose division while electrical self-energy favours it. Actual breakup depends on shape, interactions and perturbations; even the experimental split can be asymmetric. [Singh and colleagues' original study](https://arxiv.org/html/1907.02294) illustrates those dependencies. We have not declared economic cells to be charged drops.

Any adopted extension must include its actual state changes once, value the reverse consistently, and retain physical energy released into heat, motion or work in the physical balance. Tokens are not that released energy. A lower endpoint field alone does not prove that every intermediate step is favourable or fundable.

## 20. Why two different conditions can suffice

For the nonconvex field of Chapter 19, fix total reference \(S\) and resource \(X\). A collection of conditions \(z_i=x_i/s_i\) with fractions \(\lambda_i=s_i/S\) obeys

\[
\sum_i\lambda_i=1,\qquad
\sum_i\lambda_i z_i=X/S.
\]

Its complete field is \(S\sum_i\lambda_i f(z_i)\).

Assume the permitted ratios form a compact interval, \(f\) is continuous, and the ideal permits arbitrary fractions without interface or access restrictions. Then a minimum can be attained with at most two distinct ratios.

To prove it, begin with a finite mixture of at least three distinct ratios with positive fractions. There is a nonzero vector \(v_i\) satisfying

\[
\sum_i v_i=0,\qquad \sum_i v_i z_i=0,
\]

because there are more unknowns than the two linear constraints. Replace each fraction by \(\lambda_i+t v_i\). Both totals stay fixed. The complete field is linear in \(t\), so choose the sign that does not increase it. Continue until one fraction reaches zero, keeping the others nonnegative.

Remove that fraction and repeat. At most two distinct ratios remain, with no greater field. The set of two-ratio mixtures, including coincident ratios and zero fractions, is compact, so continuity supplies a minimum. Since every finite mixture can be reduced without increasing its value, this minimum is global over the ideal finite mixtures.

The selected fraction is not arbitrary. For \(z_1<X/S<z_2\), conservation gives

\[
\lambda=\frac{z_2-X/S}{z_2-z_1}.
\]

At a differentiable interior optimum, varying the ratios and fraction also gives the common-tangent condition

\[
f'(z_1)=f'(z_2)
=\frac{f(z_2)-f(z_1)}{z_2-z_1}.
\]

For global optimality, the corresponding line must lie below the curve throughout the permitted interval; stationarity alone is insufficient.

This is a meaningful binary-looking result, but its meaning is **two distinct conditions**, not two physical cells, binary reproduction or Fibonacci counts. Many cells can share each condition. Whole-unit or fixed-size restrictions can prevent the required fraction changes.

The physical phase-separation analogy is useful precisely because it distinguishes conditions, amounts and interfaces. It does not let us infer a biological division schedule from the number two.

## 21. The charged-drop endpoint calculation

For this comparison only, consider a conducting spherical liquid drop of radius \(R\), charge \(Q_{\rm e}\), surface tension \(\gamma\), and surrounding permittivity \(\epsilon_{\rm e}\).

Its surface energy is \(A=4\pi\gamma R^2\); its electrostatic self-energy is \(B_{\rm e}=Q_{\rm e}^2/(8\pi\epsilon_{\rm e}R)\). These are physical energies, not EBU reference amounts. The electrical expression follows by integrating the charging voltage of a sphere. [Feynman, electrostatic energy](https://www.feynmanlectures.caltech.edu/II_08.html).

Compare endpoints consisting of \(n\) equal spherical drops with the same total liquid volume and total charge, assigning charge \(Q_{\rm e}/n\) to each. Their radius is \(R/n^{1/3}\). Assume they are sufficiently separated for mutual electrical interaction to be negligible. Summing the separate energies gives

\[
\mathcal O_n=A n^{1/3}+B_{\rm e}n^{-2/3}.
\]

The first term increases because the complete exposed surface is larger. The second decreases because charge is spread among separate smaller charges.

Treating \(n\) temporarily as continuous,

\[
\frac{d\mathcal O_n}{dn}
=\frac13n^{-5/3}(An-2B_{\rm e}).
\]

The preferred equal-drop count in that continuous endpoint comparison is \(2B_{\rm e}/A\), with integer feasible counts checked separately. Two equal drops have lower endpoint energy exactly when

\[
\frac{B_{\rm e}}A>
\frac{2^{1/3}-1}{1-2^{-2/3}}.
\]

This is not the physical instability threshold for a small shape disturbance, nor a prediction of a breakup path. Intermediate deformations, finite-separation interactions, motion and heat can matter. Actual charged-drop breakup can be asymmetric and affected by external perturbations. [Singh and colleagues](https://arxiv.org/html/1907.02294).

The lesson for EBU is a mechanism, not a borrowed cell identity: a justified separation can lower one represented contribution more than it raises another. Its threshold follows from those contributions. A resource cell without these physical properties cannot inherit the drop's exponents merely by analogy.

The same distinction explains why a split might have a favourable final value yet need an initially costly step. Endpoint gain, local instability and the accessibility of a path are different mathematical questions.

## 22. Why this organisation field does not select one unequal fraction forever

For \(h(u)=a u^p+b u^q\) with \(p>1>q>0\), compare two parts of a total \(U\), with fractions \(\alpha,1-\alpha\). An interior optimum satisfies

\[
a p U^{p-1}
[\alpha^{p-1}-(1-\alpha)^{p-1}]
+b q U^{q-1}
[\alpha^{q-1}-(1-\alpha)^{q-1}]=0.
\]

Fix an unequal fraction \(\alpha\ne1/2\). Both bracketed expressions are nonzero, with opposite signs. Dividing by \(U^{q-1}\) shows that stationarity fixes one value of \(U^{p-q}\).

Thus, with fixed coefficients, the same unequal fraction cannot be an interior stationary optimum for every parent size. In particular, choosing a golden fraction at one size does not prove that this physical candidate favours golden splitting throughout growth.

Equal halves are stationary by symmetry at every size, though stationarity alone does not establish that they are always best. Boundary optima, whole-unit restrictions and comparisons with more than two parts still need examination.

This is a limitation of this specified candidate family, not a theorem that no physical model can ever favour a repeated unequal fraction.

<a id="growth-connections"></a>

# Part VI — Further results for growth and connections

## 23. An exact law for replacing something that must keep working

Consider a recoverable resource allocation \(q_k\) currently occupied by a task. The next allocation \(q_{k+1}\) must be prepared before the old one is released. This is a precise model of preserving existing service during a change.

Assume free resource is compatible, accessible and recombinable; the old allocation is released intact; no other task uses it; and capability is sufficient for the comparison. This does not describe recovering burned fuel or eaten food without work.

If total available stock is \(M\), the free amount is \(M-q_k\). The next allocation fits exactly when

\[
\boxed{M\ge q_k+q_{k+1}.}
\]

Necessity is immediate: both allocations coexist. For sufficiency, prepare the new amount from the free stock, activate it, and release the old amount. The new free amount is \(M-q_{k+1}\), restoring the same form for the next replacement.

Induction gives the exact minimum stock for a prescribed sequence with at least one replacement:

\[
\boxed{M_{\min}=\max_k(q_k+q_{k+1}).}
\]

This is a useful growth law that does not depend on a preferred catalogue.

If new input is permitted and current stock is \(M_k\), the least additional amount before the next replacement is

\[
D_k=\max(0,q_k+q_{k+1}-M_k).
\]

Afterward,

\[
M_{k+1}=\max(M_k,q_k+q_{k+1}).
\]

The proof is the same coexistence requirement. No historical piece is counted twice.

These formulas minimise required stock and extra input for the **same specified sequence**. They do not directly maximise EBU; field changes occur where actual resource changes are represented.

They nevertheless answer an important part of the local-growth question. A system can preserve its occupied allocation, prepare only what is missing, and reuse what is released. The additional requirement is measurable. Whether Fibonacci organisation makes this possible with fewer permitted rearrangements depends on actual piece restrictions beyond this freely recombinable ideal.

## 24. Preparing fractions for uncertain deliveries

Prepare a neutral split with fractions \(\alpha_i\) before deliveries are known. The parts begin at the same slope. The new question is which fractions maximise the expected complete contribution when future deliveries have a stated probability distribution.

Suppose the complete changes \(Q_i\) have fixed distributions independent of the chosen fractions, and let

\[
v_i=\mathbb E[Q_i^2]>0.
\]

For a fixed design interval and equal other contributions, maximising expected complete EBU requires minimising \(\sum_i v_i/\alpha_i\). Again Cauchy–Schwarz gives

\[
\sum_i\frac{v_i}{\alpha_i}
\ge\left(\sum_i\sqrt{v_i}\right)^2,
\]

with equality at

\[
\boxed{\alpha_i=\frac{\sqrt{v_i}}{\sum_j\sqrt{v_j}}.}
\]

The squares matter: variability as well as average demand affects this criterion. Golden shares arise only for corresponding second moments. These are assumed demand statistics, not values that a Gaussian calibration of \(K\) automatically supplies.

## 25. What bounded input permits

Suppose every nonempty cell needs at least \(\varepsilon\), initial resource is \(X_0\), and the external supply is at most \(P_s\) joules per second. Then, even before allowing for consumption,

\[
\boxed{N(t)\varepsilon\le X_0+P_st.}
\]

At equally spaced times this is a linear upper bound. Fibonacci counts grow exponentially and therefore cannot continue forever under these premises. Fibonacci **sizes**, bounded periods of Fibonacci counts, or stages separated by increasing times are different claims and are not excluded by this argument.

The external source thus constrains which growth histories are feasible. It does not choose a special count sequence solely through its existence.

## 26. Exactly how much improvement a limited connection leaves inaccessible

Take cells A and B with slope difference \(\delta=m_A-m_B>0\). Suppose at most \(L\) joules can be transferred from A to B in the comparison, with other feasibility conditions satisfied.

Write \(k=K_A+K_B\). Using the established two-cell finite-transfer law, the complete field reduction is

\[
R(q)=\delta q-\frac12kq^2.
\]

Its unrestricted maximum occurs at \(q^*=\delta/k\). The best allowed amount is

\[
\widehat q=\min(L,q^*).
\]

Complete the square:

\[
R(q)=\frac{\delta^2}{2k}-\frac k2(q-q^*)^2.
\]

The initial difference could permit a reduction \(\delta^2/(2k)\). After the best limited exchange, the part of that difference left is

\[
\boxed{R_{\rm left}
=\frac{[\max(\delta-kL,0)]^2}{2k}.}
\]

This is a genuine threshold derived from the field. Increasing \(L\) helps until \(L=q^*\). Beyond that point, extra connection allowance does not improve this particular initial pair any further.

The result also works for two internally equalised groups, using their total response scales \(C_A,C_B\) and their common group slopes. Their effective stiffnesses are \(1/C_A,1/C_B\). Internal restrictions can make that simplified group comparison unattainable.

## 27. How graph structure exposes an improving opportunity

Consider a finite connected resource-access graph with at least two cells. Every edge permits the pairwise exchange in either direction. In the following comparison each isolated pair equalisation is feasible. The graph can be connected while its immediate neighbouring opportunities reveal only a small part of its total unevenness.

Let

\[
R=\frac12\sum_i c_i(m_i-\bar m)^2
\]

be the total field above the equal-slope minimum. For each edge \(e=\{i,j\}\), its best isolated pair reduction is

\[
g_e=\frac{(m_i-m_j)^2}{2(K_i+K_j)}
=\frac12w_e(m_i-m_j)^2,\qquad
w_e=\frac{c_ic_j}{c_i+c_j}.
\]

Assume those isolated equalisation amounts are feasible. Define

\[
\lambda=
\min_{\substack{z\ne0\\\sum_i c_i z_i=0}}
\frac{\sum_{\{i,j\}}w_{ij}(z_i-z_j)^2}
{\sum_i c_i z_i^2}.
\]

This dimensionless number compares differences visible on allowed edges with differences across the whole graph.

Why is it positive? Normalise the denominator to one. The resulting set is compact in finite dimensions, so a minimum exists. A zero numerator would force equal \(z\) values along every edge, hence everywhere by connectivity. Their zero weighted mean would then force all values to zero, contradicting the normalisation.

Substitute \(z_i=m_i-\bar m\). It follows that

\[
\sum_e g_e\ge\lambda R.
\]

If there are \(M\) edges, the largest candidate is at least their average:

\[
\boxed{\max_e g_e\ge\frac{\lambda}{M}R.}
\]

This is a graph-dependent guarantee about the best available isolated opportunity. It is not a speed of response. The sum of candidate improvements is not an amount that can be posted: different pair candidates overlap and are alternatives calculated at one state.

For a concrete graph family, put \(N\ge3\) equal-response-scale cells in a chain, with slopes increasing by a fixed amount \(a\) from one cell to the next. Centre them so the mean slope is zero, and choose references and allowed amounts so the compared transfers are feasible. Each neighbouring pair offers \(ca^2/4\), while

\[
R=\frac{ca^2N(N^2-1)}{24}.
\]

Thus each such opportunity is only \(6/[N(N^2-1)]\) of the total. A long chain can contain substantial unevenness while every immediate neighbouring opportunity is small.

Adding a permitted direct connection between its ends creates a candidate with \((N-1)^2\) times that pair value. This proves a state-dependent advantage, not that long physical connections are free or that dense graphs are always best.

## 28. The amount required through each tree connection

On a tree, each edge is the sole connection between the two groups formed by removing it. Suppose desired net resource changes are \(b_i\), positive for net receipt, with \(\sum_i b_i=0\). Choose one side \(S_e\) of an edge \(e\). Then its required signed net incoming amount is

\[
\boxed{q_e=\sum_{i\in S_e}b_i.}
\]

No choice of internal routing can change that amount. Additional back-and-forth transfers only increase gross handling.

For the equal-slope target, \(b_i=c_i\bar m-d_i\), hence

\[
\boxed{q_e=C_{S_e}\bar m-D_{S_e},}
\]

where \(C_{S_e}=\sum_{i\in S_e}c_i\) and \(D_{S_e}=\sum_{i\in S_e}d_i\).

If the edge allows at most \(L_e\), a necessary condition for this target is

\[
|C_{S_e}\bar m-D_{S_e}|\le L_e.
\]

On a tree these conditions also suffice for a net-flow assignment. They do not alone prove a feasible sequence respecting every intermediate stock and account condition.

~~~text
      A             D
      |             |
      B ---- e ---- C ---- F

For the group {A,B}, all required net receipt
must cross e. No internal rearrangement changes that total.
~~~

For a general graph, several edges can cross the same cut. Their combined permitted amounts bound what can reach the group. An extra internal edge does not overcome an insufficient connection across the boundary.

This is a particularly useful test for splitting. A split that creates more local cells but leaves the same insufficient external connection has not solved the supply problem. A split that makes genuinely separate permitted access usable may change the feasible amount.

Nothing in this argument selects the next recipient or tells actors to travel. It tells us what any successful set of resource operations must accomplish.

## 29. Handshaking, Euler and Hamilton: what they contribute

The two-ended count behind the handshaking lemma gives an additional law for energy handling. Let \(h_i\) be the gross amount handled at cell \(i\), counting resource entry and exit positively. If \(Q_{\rm internal}\) is the total amount transferred between represented cells, and \(Q_{\rm boundary}\) the gross amount crossing the system boundary, then

\[
\boxed{\sum_i h_i=2Q_{\rm internal}+Q_{\rm boundary}.}
\]

Each internal transfer uses both a sending and a receiving endpoint. If every cell has a **total entry-plus-exit** allowance \(H_i\), this gives a necessary bound

\[
2Q_{\rm internal}+Q_{\rm boundary}\le\sum_iH_i.
\]

These total allowances must not be confused with a one-direction receiving allowance used earlier.

An Euler route uses every edge once. In a finite undirected graph whose nonisolated vertices are connected, a closed Euler route exists exactly when every degree is even; an open one with distinct endpoints exists exactly when two degrees are odd. Entries and exits pair at intermediate vertices, proving necessity. For sufficiency in the even case, follow unused edges until returning to the start; parity prevents getting stuck elsewhere. If edges remain, connectivity lets another closed route be spliced into the first. For two odd vertices, add an edge between them, construct a closed route, then remove that edge. [MIT's graph-theory chapter](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-fall-2010/f471f7b7034fabe8bbba5507df7d307f_MIT6_042JF10_chap05.pdf) develops these standard counting and route ideas.

A Hamilton cycle instead visits every vertex once and returns to the start. It concerns visiting cells, not using every connection. A standard sufficient condition for a simple graph with \(N\ge3\) is minimum degree at least \(N/2\), known as Dirac's condition. It is sufficient, not necessary: a large simple ring has a Hamilton cycle with degree two. [Morris's graph-theory text](https://www.cs.uleth.ca/~morris/Combinatorics/html/sect_Euler-Hamilton.html) states the condition and its context.

For completeness, the proof is short. Take a longest path \(v_1,\ldots,v_k\). All neighbours of its endpoints lie on it. There must be an index \(i\) for which both \(v_1v_{i+1}\) and \(v_iv_k\) are edges; otherwise the two endpoint degrees sum to at most \(k-1\), contradicting their sum being at least \(N\ge k\). Those edges close a cycle containing the entire path. The degree condition also ensures connectivity. If any vertex lay outside the cycle, connectivity would extend it into a longer path, a contradiction. Hence \(k=N\).

These route theorems do not establish sufficient resource, power, EBU holdings or beneficial field changes. They become useful when a particular task really requires visiting every cell or using every connection. There is no general EBU requirement to do either.

## 30. Which route properties survive a local division?

If an original node has \(d=a+b\) external connections, give \(a\) to A, \(b\) to B, and add A–B. The new degrees are \(a+1,b+1\). If the old graph had all even degrees, this local split preserves that property exactly when \(a,b\) are both odd. Thus an organisation change can preserve or destroy an Euler-route property independently of its field neutrality.

More generally, replace one node by \(r\) nodes connected internally as a tree, retaining its original external edges. Vertex count rises by \(r-1\), and edge count rises by \(r-1\). The number

\[
M-N+1
\]

for a connected undirected graph is unchanged. It counts independent cycles. Splitting a node into an internal tree therefore does not create additional cycle redundancy.

This distinction is economically useful. More cells can mean finer local allocation without more alternative routes. Extra route resilience requires additional genuine connections, not merely more boxes.


For an original node of degree four, the two possibilities can be shown directly:

~~~text
Give the parts 1 and 3 external connections:
    A has degree 2, B has degree 4 after adding A--B.
    Both degrees remain even.

Give the parts 2 and 2 external connections:
    A has degree 3, B has degree 3 after adding A--B.
    Two odd degrees replace the original even degree.
~~~

Both resource splits may preserve the field. Only the first preserves the condition for a closed Euler route when all other degrees are even. The graph property and the field property impose different checks on the same division.

<a id="many-operations"></a>

# Part VII — Many simultaneous and repeated operations

## 31. Repeated merging can handle the same resource many times

Take \(n\) free compatible pieces with amounts \(u_i>0\). Suppose, for this comparison, every merge physically transfers all its inputs into a new receiving cell.

A direct permitted many-way merge handles total amount \(U=\sum_i u_i\) once. A binary sequence can be drawn as a tree. If piece \(i\) passes through \(d_i\) merges before reaching the final cell, its amount is handled \(d_i\) times. Therefore

\[
L_{\rm binary}=\sum_i u_i d_i\ge U.
\]

For \(n>2\), at least one leaf has depth greater than one, so the inequality is strict. This is a proved difference in actual handling under the stated transfer interpretation, not a fee attached to the drawing.

If merging changes only permitted access and involves no such resource transfers, this meter does not apply. If a direct many-way merge is physically unavailable, it is not a competitor.

The strongest conclusion is methodological: expensive rearrangement makes the permitted operations important. It does not automatically make binary or Fibonacci rearrangement cheapest. Every allowed alternative must be included in a claimed optimum.

## 32. Computing the value of many identified actions

The value of an identified current change depends on the current state, not a replay of the complete economic history. For one quadratic cell, evaluating its current slope or exact specified endpoint difference requires a fixed number of elementary arithmetic operations.

For a finite action affecting \(n\) explicitly listed cells, summing their field changes takes work proportional to that list length, in an ideal fixed-precision arithmetic model. If the action is decomposed among \(A\) identified contributions, reading and accumulating that attribution information also takes work. No formula can certify infinitely many arbitrary supplied terms by pretending they were one known finite term.

These are counting observations about evaluating a specified description. They do not impose a request queue, choose who obtains resource, or establish the speed of a physical computing device. Exact real-number arithmetic is itself a mathematical ideal; a later implementation must handle precision and representation without claiming that numerical error is new EBU.

Parallel contributions remain governed by the established same-current-field rule. Dividing one actual change among more participants cannot multiply its complete contribution. Nor does a growing number of price queries imply a growing amount of physical resource.

For infinitely many contributions, the relevant sum or integral needs a justified convergence condition. Absolute convergence is a sufficient condition for freely reordering a scalar sum. Without such conditions, changing how an infinite collection is grouped can change or destroy its proposed value. Finite real operations do not acquire that ambiguity; the infinite ideal must be checked separately.

This gives a clean boundary for future computation: preserve exact finite laws first, specify attribution rather than infer it from endpoints, and treat infinite limits as mathematics requiring convergence—not as a promise of infinite bandwidth.

<a id="remaining-decisions"></a>

# The decisions that remain

The half-unit condition identifies a limit of whole-unit improvement. A reachable-reference requirement would avoid some of those states, but such a requirement still needs a reason and must survive permitted redesigns. The book leaves that decision open.

An empty cell retains the imbalance attached to its reference. A creation or removal rule must therefore explain which represented economic condition appears, disappears or passes to another cell. Removing a term from the calculation cannot stand in for restoring resource.

For division, the decisive missing physical relationship is now precise: how does a permitted design make independently usable handling capability depend on its response scale? A chosen \(H(s)\) can be analysed, and the split-benefit theorem evaluates the resulting complete improvement. A particular source and cell design must still justify the relationship.

The extended-field calculations offer two further possibilities: changed curvature can favour distinct conditions, and a separately justified organisation term can select a preferred physical size. Neither result authorises changing the established field without its additional premises.

The graph results identify what limited connections leave inaccessible, what opportunity must be visible, and which route properties survive division. Together with whole units and finite handling, they give specific constraints for the next study of growth.

## Previous volumes

[EBU economic cells](EBU_ECONOMIC_CELLS.md) establishes the field, valuation and composition laws used here.

[EBU between economic cells](EBU_BETWEEN_ECONOMIC_CELLS.md) develops payments, allocation, growth and the earlier graph results.

Physical and mathematical references supporting the additional comparisons are linked beside their use in this volume.
