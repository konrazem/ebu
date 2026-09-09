# Why use an Onsager-like flow law in EBU?

**Purpose.** This is a teaching note, not a protocol, theorem, empirical
claim, or change to the EBU model. It explains why the model writes

```text
J_e = M_e [f_e - θ_e]_+,
```

and exactly what is and is not being borrowed from Onsager's work.

## The short answer

The EBU burden derivative answers a *direction* question:

> If a little more resource is sent along this permitted edge, does the
> declared local burden initially go down or up?

It does **not** answer a *rate* question:

> How many units per hour can or should actually move?

The Onsager-like law is a simple kinetic closure: it converts a local downhill
signal into a finite local flow rate. It is chosen because it is local,
interpretable, and dissipative under its stated assumptions. It is not derived
from the burden function alone, and it is not claimed to be a universal law of
nature.

## Start with the physical action, not Onsager

For a directed edge `e=(i→j)`, let `y` mean the amount withdrawn from
the source and sent during an interval. The declared action physics is

```text
x_i(y)=x_i(0)-y, ;  x_j(y)=x_j(0)+η_e y.
```

Here `η_e∈[0,1]` is the fraction that arrives. Thus, per extra source
unit sent, the source loses one unit, the destination receives `η_e`,
and `1-η_e` is lost by the represented process. This is an assumption
about the edge, not a conclusion from the burden equation.

Let `V(x)=sum_k v_k(x_k)` be the declared burden and let
`μ_k=∂ V/∂ x_k`. The chain rule gives

```text
(dV)/(dy)
= μ_i(dx_i)/(dy)+μ_j(dx_j)/(dy)
=-μ_i+η_eμ_j.
```

Define the *loss-aware edge force* as the negative directional derivative:

```text
f_e=-(dV)/(dy)=μ_i-η_eμ_j.
```

The name “force” is a convention. The precise meaning is: **the initial
burden reduction per additional source unit sent along this edge.** Positive
`f_e` means that a sufficiently small action points downhill in the
declared burden. It is neither an EBU payment nor permission to export.

## The missing question: how fast does an action happen?

The force has units of burden per stock. A flow rate has units of stock per
time. They are not the same kind of quantity.

```text
[f_e]=(burden)/(stock), ;
[J_e]=(stock)/(time).
```

If the model stopped at `f_e>0`, it would know that movement is locally
helpful but would have no answer to “one millilitre per hour, or a million
litres per second?” A kinetic law supplies that missing timescale.

The simplest local choice is linear response:

```text
J_e=M_ef_e.
```

`M_e` is the edge mobility (more intuitively: conductance or throughput
coefficient). Its units must be

```text
[M_e]=(stock^2)/(burden·time).
```

Large `M_e` means that the same downhill signal produces a larger rate;
small `M_e` means the process is slow or constricted. In the simplest
linear analogy, resistance is proportional to `1/M_e`.

Over a tick of duration `Δ t`, the amount sent is

```text
y=Δ t J_e.
```

Thus mobility determines how much can move *per unit time*. It is separate
from `η_e`, which determines how much of the sent quantity survives the
trip. A route may be fast but lossy, or slow but nearly lossless.

## Where did Onsager's idea come from?

Lars Onsager developed reciprocal relations for **irreversible processes**.
His two papers, *Reciprocal Relations in Irreversible Processes I* and *II*,
appeared in *Physical Review* in 1931. The first treated coupled examples such
as thermoelectric phenomena, electrolyte transport, and anisotropic heat
conduction, and derived a general class of reciprocal relations from
microscopic reversibility. In 1968 Onsager received the Nobel Prize in
Chemistry for the reciprocal relations bearing his name.

Near thermodynamic equilibrium, the classical framework relates several fluxes
`J_a` to several thermodynamic forces `X_b`:

```text
J_a=sum_b L_{ab}X_b.
```

Under the relevant assumptions, Onsager's result concerns the symmetry of
appropriate cross-coefficients, schematically `L_{ab}=L_{ba}`, with
time-reversal qualifications in some settings. This is stronger and more
specific than merely writing “flow is proportional to a driving signal.”

Classic physical examples include:

- electric current responding to voltage difference;
- heat flux responding to temperature gradients;
- diffusion responding to chemical-potential or concentration gradients;
- coupled heat and charge transport in thermoelectric materials.

The historical result and the EBU model must not be conflated.

## What EBU borrows — and what it does not

EBU borrows the **formal pattern** of a local flux responding to a local
downhill signal:

```text
local driving signal → local rate.
```

For a single directed EBU edge, this becomes a scalar law using `M_e`. It
does **not** by itself establish any of the following:

- that EBU burden `V` is thermodynamic free energy or entropy;
- that `f_e` is a literal thermodynamic force;
- that the full Onsager reciprocal-relations theorem applies;
- that reciprocal cross-couplings between multiple EBU flows have been
  derived;
- that a real social, ecological, or infrastructure system obeys linear
  response.

“Onsager-like” is therefore the accurate name. It says the model uses a
recognisable linear flux–force architecture, not that it has converted EBU
into classical thermodynamics.

## Why the positive-part and threshold appear

The repository's ideal directed-edge rule is

```text
J_e=M_e[f_e-θ_e]_+,
;  [z]_+=max(z,0).
```

The positive part prevents a declared one-way edge from producing negative
flow. If reverse flow is physically allowed, it should be represented by a
separate reverse edge or a properly signed bidirectional law.

`θ_e≥0` is an optional activation threshold. It creates a *dead
zone*: a small positive improvement does not initiate flow. It may represent a
declared minimum meaningful action, measurement resolution, switching burden,
or a friction-like barrier. It is not required by the chain-rule derivation.

The threshold does not make `J_e` jump in value: `J_e=0` at
`f_e=θ_e`, and it grows continuously above that point. It does make the
law non-differentiable there (a kink). If there is no independently justified
reason for a threshold, the conservative modelling choice is `θ_e=0`.

## A useful mathematical reason for the form

One can declare a convex cost of maintaining flow,

```text
Ψ_e(J)=(J^2)/(2M_e)+θ_eJ, ;  J≥0.
```

The first term says that running larger flow becomes progressively harder; the
second is a per-unit activation/friction-like term. During an infinitesimal
time, transport contributes approximately `-f_eJ` to the rate of change of
burden. Balancing flow difficulty against burden reduction means minimizing

```text
Ψ_e(J)-f_eJ
```

over `J≥0`. Its minimizer is exactly

```text
J_e=M_e[f_e-θ_e]_+.
```

This is a rationale for the law, not proof that a particular real edge has
this cost function. A different measured kinetic law implies a different
`Ψ`, and therefore a different flux rule.

## Time, delay, capacity, and why they matter

A small mobility means slow throughput: little resource moves in one tick,
while demand, leakage, regeneration, and other dynamics continue. A locally
beneficial route can therefore be too slow to avert failure.

However, the simple rule models **slow rate**, not a literal travel delay. It
assumes that material sent during a tick is received within that tick, with
fraction `η_e` surviving. If travel time is material, a real model needs
an in-transit stock or a delay law: source withdrawal, edge storage/loss, and
destination arrival must be separate events. Likewise, hard capacity,
congestion, queues, hysteresis, or discrete dispatch require nonlinear or
hybrid kinetics rather than an unrestricted linear law.

This distinction matters for locality. The graph says *which* endpoints may
interact. Frozen synchronous evaluation and finite edge rates constrain *when*
effects propagate. Mobility alone does not guarantee locality: a long-distance
edge with high `M_e` is still a fast nonlocal connection.

## How this fits the EBU sequence

The pieces have distinct jobs:

```text
declared transfer physics
→
burden derivative f_e
→
kinetic request J_e
→
physical permission
→
finite EBU quote.
```

1. **Transfer physics** declares what sending does to stock, including loss.
2. **Force** says whether an infinitesimal permitted transfer initially lowers
   the declared burden.
3. **Mobility law** proposes a rate; it does not settle value or certify
   safety.
4. **P1C or another preservation layer** can reduce or refuse the request if
   the source cannot safely export.
5. **The exact finite EBU quote** evaluates an accepted finite action rather
   than treating its initial slope as final settlement:

   ```text
   Δe_field(y) = V_local(z) - V_local(z + yS_e).
   ```

   where `z` is the no-action baseline. When the path is valid, the exact
   field change is the integral of the changing marginal force:

   ```text
   Δe_field(y) = integral from 0 to y of f_e(s) ds.
   ```

The force is therefore the **marginal bridge** between physical state and EBU
valuation. It is not itself an EBU balance, a moral score, or a promise that
an action is feasible.

## A defensible answer to “Why choose Onsager?”

> We use an Onsager-like law as the smallest local kinetic closure. The
> chain-rule derivative gives a local direction of declared burden reduction,
> but cannot determine a rate. A linear mobility law turns that signal into a
> rate with an explicit timescale and edge-specific throughput. It is chosen
> for transparency, locality, and dissipative consistency—not because EBU has
> proved that its burden is thermodynamic free energy or that Onsager
> reciprocity universally applies. In a real application, mobility, loss,
> capacity, delay, and the burden shape must be independently measured or
> validated; otherwise this is a hypothesis to test, not a discovery.

## Questions that a real application must answer

Before treating the law as more than a teaching or exploratory model, ask:

1. What real stock does `x` measure, and in what units?
2. Are the allowed edges and their directions physically or institutionally
   real?
3. Is `η_e` measured as a survival/yield fraction?
4. Is `M_e` measured from throughput data, or only guessed?
5. Is there a measurable reason for `θ_e`, or should it be zero?
6. Are travel delay, capacity, queues, and storage on the edge negligible at
   the chosen time resolution?
7. Does the selected burden function predict the declared physical outcome
   better than credible alternative shapes?
8. Do decisions generated by the model outperform predeclared baselines on
   held-out or preregistered cases?

A “no” or “unknown” answer is not a reason to hide the model. It is the next
research task, and it limits the claim that may be made today.

## Sources for the historical claim

- Lars Onsager, “[Reciprocal Relations in Irreversible Processes. I](https://doi.org/10.1103/PhysRev.37.405),” *Physical Review* 37, 405–426 (1931). The
  original paper describes coupled irreversible processes and its theoretical
  basis.
- Lars Onsager, “[Reciprocal Relations in Irreversible Processes. II](https://doi.org/10.1103/PhysRev.38.2265),” *Physical Review* 38, 2265–2279 (1931).
- [Nobel Prize in Chemistry 1968: Lars Onsager](https://www.nobelprize.org/prizes/chemistry/1968/summary/), for the official award citation.
- [Onsager's Nobel lecture](https://www.nobelprize.org/uploads/2018/06/onsager-lecture.pdf), for his retrospective account of the 1929 announcement and 1931 exposition.

## Related EBU sources in this repository

- `d0_v29.py`: the frozen local law implements
  `f_e=μ_i-η_eμ_j` and `J_e=M_e[f_e-θ_e]_+`.
- `V3.0_LOCAL_EBU_FOUNDATION_DRAFT.md`: distinguishes local force, physical
  permission, and the exact pre-action finite quote.
- `README.md`: states the scope and limitations of the D0 and P1C work.
