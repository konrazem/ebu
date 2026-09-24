## Verdict

**The finite-change mathematical core survives this independent audit.** Two stronger claims do not follow from it:

- Exact simultaneous attribution is **not uniquely determined by physical state and conservation**.
- Individual owner accounts are **not generally functions of the current physical state**, even when aggregate accounting is exact.

The Gaussian potential and the definition of EBU are modeling choices. Once those are declared, the identities below follow mathematically. That distinction must remain explicit.

I did not use prior audit conclusions as proof. The checks were newly derived, deterministic, exact-rational or polynomial calculations. No demand rules, affordability constraints, simulations or account-settlement routines entered the derivations.

### Verification scope

Published mechanism: `2c4b71d15fe8cb46592d9f2ead8f5f4e62fe9e32`.

- **24,336 independent mathematical comparisons: zero mismatches.**
- **47,140 comparisons against the published pure mathematical implementation: zero mismatches.**
- General Gaussian cases: **720**, dimensions 1–6, unequal rational references and scales.
- Study-1 physical domain: **91 states, 3,662 source-funded nonempty groups**, including groups with zero net increment.
- Owner-loop search: **576 directed two-action reverse-transfer loops**, of which **528 redistribute between source-assigned accounts**.

These are exhaustive counts only for the specified finite domains—not computational proofs over all possible states or functions.

## 1. Independent derivation of the core

Let \(r=x^*\), with every \(\sigma_i>0\), and declare

\[
V(x)=\frac12\sum_i\frac{(x_i-r_i)^2}{\sigma_i^2}.
\]

Differentiation gives

\[
\boxed{\mu_i(x)=\frac{x_i-r_i}{\sigma_i^2}},
\qquad
\boxed{H_{ij}=\frac{\delta_{ij}}{\sigma_i^2}}.
\]

The exponent is **two**, not one.

Define the signed finite value by

\[
E(x,\Delta):=V(x)-V(x+\Delta).
\]

This is a definition of the measured quantity, not something conservation alone forces us to choose.

### Derivation A: direct expansion

For each coordinate,

\[
(x_i+\Delta_i-r_i)^2
=(x_i-r_i)^2+2(x_i-r_i)\Delta_i+\Delta_i^2.
\]

Subtracting the potentials yields

\[
\boxed{
E=-\mu(x)^\top\Delta-\frac12\Delta^\top H\Delta.
}
\]

No approximation or small-action assumption occurs.

### Derivation B: fundamental theorem along a line

Set \(\gamma(\lambda)=x+\lambda\Delta\). Then

\[
\frac{d}{d\lambda}V(\gamma(\lambda))
=\nabla V(\gamma(\lambda))^\top\Delta.
\]

For this quadratic potential,

\[
\nabla V(x+\lambda\Delta)=\mu(x)+\lambda H\Delta.
\]

Therefore,

\[
E=-\int_0^1(\mu+\lambda H\Delta)^\top\Delta\,d\lambda
=-\mu^\top\Delta-\frac12\Delta^\top H\Delta.
\]

The polynomial expansion and the line-integral derivation agree. All **720 general cases** and **3,662 Study-1 physical groups** matched exactly.

## 2. General edge equation and its restricted simplification

For a lossless transfer of quantity \(q\) from \(s\) to \(d\),

\[
\Delta_s=-q,\qquad \Delta_d=q,
\]

so

\[
\boxed{
E=
q\left[
\frac{x_s-r_s}{\sigma_s^2}
-\frac{x_d-r_d}{\sigma_d^2}
\right]
-\frac{q^2}{2}
\left[
\frac1{\sigma_s^2}+\frac1{\sigma_d^2}
\right].
}
\]

This allows unequal references and unequal scales.

If both references agree and both scales equal a common \(\sigma\),

\[
E=\frac{q(x_s-x_d-q)}{\sigma^2}.
\]

Consequently,

\[
\boxed{E=q(x_s-x_d-q)}
\]

is an identity for all relevant stocks and quantities only under the common-reference, **unit-scale numerical normalization**. Accidental equality at an individual state does not establish that identity generally.

Exact counterexamples, both using \(x=(6,4)\), \(q=1\):

| References | Scales | General equation | Unlicensed simplified equation |
|---|---|---:|---:|
| \((0,0)\) | \((2,1)\) | \(-25/8\) | \(1\) |
| \((5,4)\) | \((1,1)\) | \(0\) | \(1\) |

The properly restricted Study-1 specialization passed **576 executable directed-transfer checks**.

## 3. Edge force, efficiency and the loss coordinate

With

\[
\frac{dx_s}{dq}=-1,\qquad
\frac{dx_d}{dq}=\eta,
\]

the chain rule gives

\[
\frac{dV}{dq}=-\mu_s+\eta\mu_d.
\]

If “driving force” means **potential decrease per additional source quantity**, its sign convention is

\[
\boxed{f_e=-\frac{dV}{dq}=\mu_s-\eta\mu_d.}
\]

This does not itself establish a physical motion law.

### Essential qualification

If the lost quantity enters a represented coordinate \(\ell\),

\[
\frac{dx_\ell}{dq}=1-\eta,
\]

and that coordinate contributes to \(V\), then

\[
\boxed{
f_e=\mu_s-\eta\mu_d-(1-\eta)\mu_\ell.
}
\]

The two-coordinate expression remains correct when the loss coordinate is outside \(V\), or its contribution vanishes. It is incomplete otherwise.

For example, with unit scales,

\[
x=(6,5,2),\quad r=(4,4,0),\quad \eta=\frac12,
\]

the full force is \(1/2\), whereas omitting the sink gives \(3/2\). Exact finite differences satisfy

\[
\frac{E(q)}q=\frac12-\frac34q,
\]

which approaches \(1/2\), not \(3/2\).

**120 general loss-aware derivative checks and 360 small-quantity checks passed.**

A valued loss coordinate also does **not** imply the whole action must have negative EBU: improvements elsewhere can outweigh its contribution.

## 4. Finite versus differential value

For positive Gaussian scales,

\[
E-(-\mu^\top\Delta)
=-\frac12\Delta^\top H\Delta\le0,
\]

strictly negative for nonzero \(\Delta\).

Thus the initial-gradient expression overestimates finite potential reduction. It can even have the wrong sign.

For unit scales and references \((4,4)\):

| Initial state | Transfer \(s\to d\) | Initial-gradient estimate | Exact finite EBU |
|---|---:|---:|---:|
| \((4,4)\) | \(q=1\) | \(0\) | \(-1\) |
| \((6,4)\) | \(q=1/10\) | \(1/5\) | \(19/100\) |
| \((6,4)\) | \(q=1\) | \(2\) | \(1\) |
| \((6,4)\) | \(q=3\) | \(6\) | \(-3\) |

The negative correction is guaranteed for this positive-definite quadratic potential. It is not a universal sign theorem for arbitrary nonconvex potentials.

## 5. Path independence and simultaneous attribution

For a globally defined \(C^1\) potential and a piecewise-smooth path \(\gamma\) lying in its domain,

\[
\boxed{
V(a)-V(b)
=-\int_\gamma\nabla V\cdot dx.
}
\]

This follows directly from the chain rule. No simply-connected-domain assumption is needed **when a single-valued potential is already given**.

A topology objection to an arbitrary curl-free vector field does not overturn this statement about an actual gradient.

### Common-path receipts

Let \(\Delta_G=\sum_a\Delta_a\), with fixed action increments, and define

\[
R_a=-\int_0^1
\nabla V(x+\lambda\Delta_G)^\top\Delta_a\,d\lambda.
\]

Linearity gives

\[
\sum_aR_a
=-\int_0^1\nabla V(x+\lambda\Delta_G)^\top\Delta_G\,d\lambda
=\boxed{E_G}.
\]

For the Gaussian potential,

\[
\boxed{
R_a=-\mu(x)^\top\Delta_a
-\frac12\Delta_a^\top H\Delta_G.
}
\]

These formulas passed the full finite-domain receipt checks. Closure also passed **80 nonquadratic, nonseparable polynomial cases**.

### Exact does not mean unique

Take \(V(x)=\frac12\|x\|^2\),

\[
x=(2,0,0),\quad
\Delta_a=(-1,1,0),\quad
\Delta_b=(-1,0,1).
\]

Total EBU is \(1\), but:

- common-path attribution: \((1/2,1/2)\);
- sequential attribution, \(a\) first: \((1,0)\);
- sequential attribution, \(b\) first: \((0,1)\), indexed by \((a,b)\).

All totals are exact.

**Classification:** common-path receipts are uniquely computed once that convention and action decomposition are specified. They are not uniquely selected by the endpoint difference or conservation alone. A claim that the common path was physically realized needs a separate physical specification.

### Quadratic Shapley equivalence

Define the mathematical subset game

\[
v(S)=V(x)-V\!\left(x+\sum_{a\in S}\Delta_a\right).
\]

For quadratic \(V\), the marginal contribution of \(a\) after subset \(S\) is

\[
-\mu^\top\Delta_a
-\frac12\Delta_a^\top H\Delta_a
-\sum_{b\in S}\Delta_a^\top H\Delta_b.
\]

In the average over all permutations, each other action precedes \(a\) with probability \(1/2\). The average therefore equals the common-path formula.

**120 complete permutation-average checks passed**, including nonseparable quadratic Hessians.

This equivalence requires fixed additive increments and a defined value for every relevant subset. It is not general for nonquadratic \(V\). For \(V(x)=x^3\), \(x=0\), and increments \(1,2\):

- common-path receipts: \((-9,-18)\);
- permutation-average receipts: \((-10,-17)\).

Both sum to \(-27\).

## 6. Refinement and conservation

### Sequential refinement

For any state function \(V\),

\[
[V(x)-V(x+\Delta_1)]
+[V(x+\Delta_1)-V(x+\Delta_1+\Delta_2)]
=V(x)-V(x+\Delta_1+\Delta_2).
\]

This is exact telescoping. It requires no demand-legality or attribution assumption.

For a quadratic potential, the different construction using the **same initial baseline twice** satisfies

\[
\boxed{
E(x,\Delta_1)+E(x,\Delta_2)
-E(x,\Delta_1+\Delta_2)
=\Delta_1^\top H\Delta_2.
}
\]

It is generally unequal to the combined finite value.

Splitting a unit transfer from equilibrium into \(m\) equal fragments:

- updating the baseline gives total **\(-1\)** for every \(m\);
- quoting every fragment at the original equilibrium gives **\(-1/m\)**.

Checked exactly for \(m=1,2,3,7,100\). The incorrect construction approaches zero as refinement increases.

### Conservation

For lossless transfer,

\[
\Delta x_s+\Delta x_d=-q+q=0.
\]

For loss-aware transfer with an explicit sink,

\[
\Delta x_s+\Delta x_d+\Delta x_\ell
=-q+\eta q+(1-\eta)q=0.
\]

Without that coordinate, the represented source-plus-destination subsystem loses \((1-\eta)q\), which must cross a declared boundary.

This conservation equation concerns one homogeneous carrier, or appropriately converted conserved quantities. Arbitrarily summing unlike physical quantities is not meaningful.

## 7. Factor potentials and Möbius interactions

For

\[
V(x)=\sum_\alpha\phi_\alpha(x_{S_\alpha}),
\]

the gradient is the sum of the embedded factor gradients, and

\[
E=\sum_\alpha
\left[
\phi_\alpha(x_{S_\alpha})
-\phi_\alpha((x+\Delta)_{S_\alpha})
\right].
\]

Only factors whose arguments change need evaluation. If \(T=\operatorname{supp}\Delta\), a sufficient touched-factor set is

\[
\{\alpha:S_\alpha\cap T\ne\varnothing\}.
\]

For a nonseparable factor, evaluate that **whole factor**, not just a supposed independent contribution of the changed coordinate.

Independent polynomial tests covered coupled cubic and quartic factors, curved paths and touched-factor cancellation:

- 80 coefficient-level chain-rule checks;
- 80 curved-path integral checks;
- 80 touched-factor checks;
- 80 factor-gradient checks;
- zero mismatches.

For fixed additive action increments, Möbius inversion decomposes the already-defined subset values:

\[
v(G)=\sum_{S\subseteq G}I(S).
\]

It creates no additional EBU.

For quadratic \(V\),

\[
v(S)=
\sum_{a\in S}
\left[-\mu^\top\Delta_a-\frac12\Delta_a^\top H\Delta_a\right]
-\sum_{\{a,b\}\subseteq S}\Delta_a^\top H\Delta_b.
\]

Therefore the highest possible nonzero interaction order is **two**.

**1,120 reconstruction checks and 240 higher-order-zero checks passed.**

This order bound does **not** automatically survive if each subset resolves a different, nonadditive action vector. Physical application also needs the relevant subsets to be admissible; algebra cannot supply missing subset experiments.

## 8. Aggregate capacity identity and owner-vector dependence

Assume

\[
C_{t+1}-C_t
=E_t
=V(x_t)-V(x_{t+1}).
\]

Then

\[
\boxed{C_{t+1}+V(x_{t+1})=C_t+V(x_t).}
\]

Required assumptions:

- one fixed potential, including fixed parameters;
- consistent state endpoints;
- exact aggregate credit equal to that finite difference;
- no omitted physical change between endpoints;
- no additional accounting source, sink or separately charged burden.

No account-nonnegativity assumption is needed.

### External events and changing fields

Suppose an external event changes \((x_t,\theta_t)\) to \((y_t,\theta'_t)\), the action then reaches \(x_{t+1}\), and an external accounting entry contributes \(J_t\). If actor EBU uses \(\theta'_t\),

\[
\boxed{
(C_{t+1}+V_{\theta'_t}(x_{t+1}))
-(C_t+V_{\theta_t}(x_t))
=
V_{\theta'_t}(y_t)-V_{\theta_t}(x_t)+J_t.
}
\]

That right-hand side must be recorded; it generally does not vanish. If the field changes during an action, its parameter-derivative contribution likewise cannot be silently omitted.

Both fixed-field telescoping and the extended identity passed **100 exact cases each**.

### Individual accounts are not generally state functions

Assume, separately, that each action’s receipt is assigned to its source owner.

At reference \((4,4,4)\):

1. `B→C@1` changes the state to \((4,3,5)\), with receipt \(-1\) assigned to B.
2. `C→B@1` returns to \((4,4,4)\), with receipt \(+1\) assigned to C.

The physical state returns exactly. Aggregate change is zero. The owner vector changes by

\[
\boxed{(0,-1,+1)}.
\]

No borrowing or account constraint enters this construction.

The exhaustive search over **576 directed reverse-transfer loops** found **528 with nonzero owner redistribution**.

Therefore:

- aggregate accounting can be a state-function difference;
- individual owner accounting generally depends on the path and assignment convention;
- aggregate cycle closure does not imply owner-by-owner cycle closure.

## 9. Units and limits

For the stated normalized potential, with coordinate units \(U_i\):

| Quantity | Units |
|---|---|
| \(x_i,x_i^*,\sigma_i,\Delta_i\) | \(U_i\) |
| \(V,E,R_a\) | dimensionless |
| \(\mu_i\) | \(U_i^{-1}\) |
| \(H_{ij}\) | \((U_iU_j)^{-1}\) |
| \(q\), for a homogeneous transfer | carrier quantity |
| \(f_e\) | inverse carrier quantity |

Thus the simplified expression \(q(x_s-x_d-q)\) silently assumes normalized coordinates/unit scale. In dimensional stocks, the appropriate scale factors cannot be dropped.

If \(V\) is assigned a physical unit rather than being dimensionless, that unit must consistently multiply \(E,R,\mu,H\). A normalized gradient is not automatically a mechanical force.

Limiting checks agree with the derivations:

- \(q\to0\): \(E/q\to f_e\).
- \(\Delta\to0\): \(E\to0\); the linearization error is quadratic.
- \(x\to x^*\): finite EBU tends to \(-\Delta^\top H\Delta/2\).
- \(\sigma_s\to\sigma_d\): the general edge equation continuously reaches the common-scale formula; reference differences remain unless separately equal.
- \(\eta\to1\): the sink increment and its force contribution vanish.
- Arbitrary sequential refinement preserves total EBU.

## 10. Required result table

“Pass” below means the conditional identity passed analytic derivation and the specified exact checks—not that its assumptions were derived from physics.

| Claim | Assumptions | Independent derivation | Exact verification | Dimensions | Limits | Counterexample / classification |
|---|---|---|---|---|---|---|
| Gaussian \(V\) | Declared references, positive scales | Definition; nonnegative squares | 720 cases | Consistent | Continuous | **Model choice**, not physical necessity |
| \(\mu=\nabla V\) | Differentiable Gaussian | Coordinate differentiation | 720 independent cases | Consistent | Pass | **Pass** |
| \(E=V_{\rm pre}-V_{\rm post}\) | Declared signed value definition | Definition | Endpoint evaluation | Consistent | Pass | **Definition**, not uniquely forced |
| Finite quadratic formula | Fixed quadratic potential | Expansion and FTC | 720 + 3,662 cases | Consistent | Pass | **Pass** |
| General edge equation | Lossless fixed increment | Substitute edge vector | 120 general cases | Consistent | Pass | **Pass** |
| Study-1 simplified edge | Equal references, unit scales | Specialization | 576 transfers | Normalized units | Pass | Fails outside hypotheses |
| Edge force | Negative directional derivative | Chain rule | 120 + 360 checks | Consistent | Pass | Valued sink requires extra term |
| Path integral | Single-valued \(C^1\) potential | Chain rule along path | 80 polynomial coefficient/integral cases | Consistent | Pass | **Pass** |
| Common-path receipts | Declared straight common path | Integral evaluation | Gaussian and 80 nonquadratic cases | Consistent | Pass | **Convention**, not unique attribution |
| Receipt-sum identity | Fixed increments sum to group | Linearity + FTC | All 3,662 groups | Consistent | Pass | **Pass** |
| Refinement | Updated intermediate baseline | Telescoping | 720 cases; explicit subdivisions | Consistent | Pass | Same-baseline summation fails generally |
| Conservation | Declared carrier increments | Sum of increments | 3,662 lossless + 120 loss-aware | Carrier-specific | Pass | Subsystem loses mass without sink/boundary |
| Factor identities | Declared differentiable factors | Sum and cancellation | 80 cases per factor check | Consistent | Pass | Nonseparable factors cannot be truncated |
| Möbius interpretation | Defined subset values; additive increments for order bound | Inclusion–exclusion | 1,120 + 240 checks | Same units as E | Consistent | Decomposition, **not extra value** |
| \(C+V\) invariant | Exact settlement, fixed field, no omitted sources | Telescoping | 100 fixed + 100 extended | \(C\) must match V units | Consistent | **Conditional accounting theorem** |
| Owner-vector path dependence | Declared source assignment | Closed-loop construction | 576 loops; 528 redistributions | Consistent | Nonzero for nontrivial loops | Owner state-function claim **false generally** |
| Affordability gate | Additional account constraint | No implication from core | Core remains consistent with signed accounts | Not a dimensional issue | Not applicable | **Not derived from physics** |

## 11. Requested physical-derivation classifications

| Rule | Classification |
|---|---|
| \(B_i\ge0\) | **NOT DERIVED FROM PHYSICS** |
| \(B_i+r_i\ge0\) before action | **NOT DERIVED FROM PHYSICS** |
| No borrowing | **NOT DERIVED FROM PHYSICS** |
| No pooling | **NOT DERIVED FROM PHYSICS** |
| Complete service | **NOT DERIVED FROM PHYSICS** |
| Additive persistent orders | **NOT DERIVED FROM PHYSICS** |
| No partial service | **NOT DERIVED FROM PHYSICS** |
| FIFO/backlog rules | **NOT DERIVED FROM PHYSICS** |

## Final independent verdicts

**A. CORE MATHEMATICS**

**INDEPENDENT SKEPTIC CONFIRMS CORE** — conditional on the declared potential, finite-value definition, fixed-field assumptions and correctly represented physical increments.

**B. ATTRIBUTION / CAPACITY**

**CONDITIONAL ACCOUNTING STRUCTURE** — common-path attribution requires its declared convention; aggregate invariance requires exact settlement and the stated source boundaries; individual owner accounts are generally path-dependent.

**C. ECONOMIC RULES**

**NOT PHYSICALLY DERIVED** — account nonnegativity, pre-action affordability, no borrowing, no pooling, complete service, persistent additive orders, no partial service, and FIFO/backlog rules.

Repository HEAD remained `6538f919…`. No files were modified, no model state advanced, and nothing was committed or pushed.
