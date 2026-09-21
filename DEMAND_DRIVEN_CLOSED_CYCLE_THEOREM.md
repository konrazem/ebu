# Closed-cycle no issuance, and the sources of aggregate capacity

**Status: PROVED FOR THIS MODEL, AND VERIFIED EXACTLY IN CONFORMANCE.**
Scope is `EBU-DEMAND-DRIVEN-ECONOMY-v1` with Capacity V1 and `C_a = 0`. The
process-burden extension in §4 is a conditional derivation and is **not
adopted**; nothing in the implementation charges a burden.

Implementation: `demand_driven_ebu/cycles.py`. Checks:
`test_demand_driven_ebu.py`, groups "closed-cycle no-issuance theorem",
"closed cycle holds for simultaneous groups", "capacity-source identity over a
driven run", "randomized closed cycles mint nothing", "repeated oscillation
mints nothing".

---

## 1. The one identity everything follows from

Write an epoch as `x_t -> y_t -> x_{t+1}`: nature acts first, the actor second.

```
E_t        = V(y_t) - V(x_{t+1})      the actor's contribution
dV_ext,t   = V(y_t) - V(x_t)          what nature injected
```

Summing over a window and telescoping,

```
sum_t E_t = sum_t [ V(x_t) + dV_ext,t - V(x_{t+1}) ]
          = V(x_0) - V(x_T) + sum_t dV_ext,t
```

Settlement is exact and the common-path receipts of the executed group sum to
its own EBU, so `delta B_total = sum_t E_t` and

```
        delta B_total = V(x_0) - V(x_T) + sum_t dV_ext,t          (*)
```

Identity (*) is exact, not asymptotic, and it is checked with tolerance zero
over driven runs in all four arms.

## 1a. Actor-only is a provenance question, not a potential question

The theorem's first hypothesis is that **no external physical transition
occurred**, and that must be decided from recorded event identities. It cannot
be inferred from `sum_t dV_ext,t == 0`.

Two external events can cancel in the potential, and an external permutation
of stock between symmetric coordinates changes the state at constant `V`. In
either case the potential term is zero while the interval plainly contained
external physical transitions, and a classifier reading only the potential
would certify a no-issuance result the theorem does not cover.

`cycles.actor_only` therefore reads `EpochRecord.external_events`, a list of
identities recorded whenever nature actually moved stock, and nothing else.
An economic demand arrival is **not** an external physical event: it moves no
stock, so it cannot break actor-only status.

The conformance gate pins all three cases. In a routeless world, where the
actor can never act, two scripted external events that cancel leave the state
returned, the potential term zero and no loss — the exact configuration the
superseded test would have called a closed actor-only cycle — and the
provenance classifier reports `EXTERNAL_PHYSICAL_EVENT_PRESENT`. A permutation
at constant `V` is likewise rejected. A genuine actor-only window, economic
arrivals included, is accepted and mints nothing.

## 2. Theorem (closed-cycle no issuance)

**Hypotheses.** No external physical transition during the cycle, decided by
provenance as in §1a; exact finite EBU; exact settlement; `C_a = 0`; and the
complete represented potential state returns, `x_T = x_0`.

**Conclusion.**

```
sum_{t=0}^{T-1} E_t = V(x_0) - V(x_T) = 0     and     delta B_total = 0.
```

**Proof.** Both right-hand terms of (*) vanish: the second by the no-injection
hypothesis, the first by state return. ∎

Repeating `A -> B -> A -> B -> A` therefore cannot mint aggregate capacity, for
any number of repetitions. Capacity may move between actors; the total cannot
grow.

**Extension to simultaneous groups.** The argument uses only telescoping and
receipt closure, and is indifferent to how many actions ran in each epoch. The
executed object per epoch is one group `G` with `sum_a R_a = E_G` exactly, so
the proof goes through verbatim. This is verified separately with two-action
out-and-back groups.

**Verified after the additive-service correction.** The theorem and the
identity were re-checked against the corrected service semantics: driven runs
with up to three simultaneous economic orders per epoch, in all four arms,
leave the capacity-source residual and both window residuals exactly zero. No
action is credited twice within an epoch, receipts sum to the epoch EBU
exactly, and no economic demand is ever served twice.

**Verified instances.** A four-step single-action loop returns the state and
leaves the opening total exactly unchanged; a two-step simultaneous
out-and-back does the same; thirty randomized out-and-back paths of length
four, generated from the declared RNG, all return the state exactly and all
leave the total exactly unchanged; and six repetitions of a two-state
oscillation never move the total off its opening value.

## 3. Corollary (loss forces the ledger, not the theorem)

Every action's increment sums to zero over **all** coordinates, sinks included.
With no external injection, the grand total of each resource is therefore
invariant. If the valued coordinates return to `x_0`, the audit-only sinks must
hold exactly what they held before:

> a closed cycle in the represented state admits **no net irreversible loss**.

A path with genuine loss is consequently not a closed cycle and must not be
called one. `cycles.closed_cycle` classifies such a path
`IRREVERSIBLE_LOSS_PRESENT` rather than reporting a failed theorem.

## 4. Process burden — a conditional derivation, not an adoption

A declared nonnegative per-action burden `C_a >= 0` is **not** part of the
accepted mechanism. It was a candidate assumption in the superseded Direction C
material, where `C_a ≡ 0` was explicitly flagged as load-bearing, and the
current authority adopts no burden.

*If* one were adopted and `R_a - C_a` were settled, the same telescoping would
give, under otherwise closed return,

```
delta B_total = - sum_a C_a  <=  0.
```

This form is recorded with its hypothesis attached. It is not implemented: an
AST check asserts that no identifier for a burden, process cost or activation
cost appears in the capacity, valuation or harness modules, and `C_a = 0`
throughout.

## 5. Capacity-source classification

Reading (*) as a table, aggregate capacity can increase in exactly two ways.

| source | effect on aggregate capacity | why |
|---|---|---|
| `EXTERNAL_PHYSICAL_DEVIATION` | may increase it | `sum_t dV_ext,t > 0`: nature injected deviation that actors were paid to remove |
| `NET_APPROACH_TO_REFERENCE` | may increase it | `V(x_0) - V(x_T) > 0`: the window ended closer to the reference than it started |
| `ECONOMIC_DEMAND_ARRIVAL` | **cannot change it** | an arrival moves no stock, so it changes no `V`, so it contributes to neither term |
| `CLOSED_ACTOR_ONLY_CYCLE` | **cannot change it** | both terms vanish |

The third row is the economically important one. **A demand is a reason to act,
never a receipt.** The conformance gate drives an epoch in which a demand
arrives, is admitted, and turns out to be unaffordable, and asserts that the
state and the capacity total are both exactly unchanged.

Externally injected deviation must be reconciled through the external ledger;
`EconomyRun.capacity_source_residual` reports the residual of (*) and is zero
in every conformance and rehearsal run.

## 6. The worked circulation examples (contract section 28)

Both are exact, hand-checkable, and asserted in the conformance gate.

### 6.1 No net issuance

World `cycle-v1`: four cells, `x* = (10,10,10,10)`, `sigma = 1`, opening
`B_total = 100` (25 each).

| step | plan | `E` | `B_total` |
|---|---|---|---|
| economic | `A->B 2`, `C->D 4` | `-20` | 80 |
| restore | `D->A 2` | `+8` | 88 |
| restore | `A->C 1`, `D->C 1` | `+7` | 95 |
| restore | `B->A 1`, `B->C 1`, `D->C 1` | `+5` | 100 |

The state returns exactly to `x*` and the total returns exactly to 100.
Capacity has moved from economic consumption to physical restoration:
`A = 23.5`, `B = 28.5`, `C = 9`, `D = 39`. No net issuance, and two actors'
balances changed in opposite directions — the same fixture serves as the
two-actor migration case.

### 6.2 Irreversible loss

World `loss-v1`: three cells plus a sink **inside** `V`; the route `A->B`
wastes half of what it carries.

| step | plan | `E` | `B_total` |
|---|---|---|---|
| economic | `A->B 4` (η = ½), `C->B 2` | `-20` | 80 |
| restore | `B->A 3`, `B->C 2` | `+17` | 97 |

Two units are irreversibly wasted. The reachable potential floor is exactly
`3` — verified by enumerating every executable plan from the post-economic
state — so `+17` is the most that can ever be earned back, and the final total
is `97`, short by exactly the unrecoverable potential. The state does not
return, so this is **not** a closed cycle and the theorem does not apply to it.

## 7. What is not claimed

- No claim that aggregate capacity is bounded over an open-ended driven run.
  Identity (*) says it tracks injected deviation, and nature's injection is not
  bounded here.
- No claim that per-owner balances are bounded, fair, or converge.
- No claim that `C_a > 0` is the right model, or that it is wrong. §4 derives
  its consequence and stops.
- No behavioural claim of any kind. This document is arithmetic about the
  mechanism, not evidence about the economy.
