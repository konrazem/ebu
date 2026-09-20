# Net-zero action groups: a null action and a capacity-transfer channel

**Status: structural finding about the registered action menu, with proofs.**
It changes no registered artifact and invalidates no registered result. It
identifies one design decision the homeostasis mission cannot freeze without an
author ruling, and it records a mechanism property that was not previously
written down.

Discovered by the mandatory-action conformance check in
`test_homeostasis_harness.py`, which asserted that no group is affordable at
the reference with zero balances and turned out to be wrong.

---

## 1. What a net-zero group is

The registered menu enumerates all nonempty groups of at most two atomic
actions on distinct ordered edges. On three cells with `quanta = {1}` that is
**21 groups**, of which **three** are *cancelling pairs*:

```
g:[a:0->1:1, a:1->0:1]      g:[a:0->2:1, a:2->0:1]      g:[a:1->2:1, a:2->1:1]
```

Each is a nonempty group of two real transfers whose summed increment is
exactly zero. Under `ActionGroup`'s rules they are entirely legitimate: the two
actions sit on distinct ordered edges `(i,j)` and `(j,i)`, so they are not
duplicates.

## 2. Theorem N1 — a net-zero group is physically inert and exactly free

Let `G = {a, a'}` with `a = (i -> j, q)` and `a' = (j -> i, q)`. Then
`delta_G = 0`, and for any state `z` the common-path receipts are

```
R_a  = -mu(z)^T delta_a - (1/2) delta_a^T H delta_G = -mu^T delta_a = q(mu_i - mu_j)
R_a' = -R_a
E_G  = R_a + R_a' = 0
```

exactly, at every state. With `owner(a) = src(a)`:

```
Delta B_i = +q(mu_i - mu_j)        Delta B_j = -q(mu_i - mu_j)        x unchanged
```

**Corollary N1.1 (free at the reference).** At `x = x*` every `mu_i = 0`, so
`Delta B = 0` for both owners. The three net-zero groups are therefore
*unconditionally affordable at the reference*, while every one of the other 18
groups has a strictly negative owner delta there and is unaffordable from zero
balances. Verified by enumeration in the conformance suite.

**Corollary N1.2 (a capacity transfer).** Away from the reference the same
inert group moves

```
T = q (mu_i - mu_j) = q (z_i/sigma_i - z_j/sigma_j)
```

units of capacity from owner `j` to owner `i`, with **no physical change at
all**. Capacity flows toward the cell that is further above its reference. The
transfer is bounded only by the payer's balance, since affordability requires
`B_j >= T`. Worked instance, verified: at `x = (12, 9, 9)` the group
`{0->1, 1->0}` has `E_G = 0` and owner deltas `{0: +3, 1: -3}`.

## 3. Why each corollary matters

### 3.1 Mandatory action is satisfied in letter, not in substance

Mission section 6 freezes: *"An actor may not preserve homeostasis simply by
refusing all physical demand."* A cancelling pair is not a voluntary
abstention, a wait or a no-op added as a policy — it is two real transfers that
genuinely execute. No rule in section 6 is broken by its presence. But its
physical effect is identical to refusal, and by Corollary N1.1 it is always
available at the reference at zero cost.

So an actor that has reached `x*` can remain there indefinitely while formally
acting every tick. Measured on a 48-tick conformance probe at `p_force = 1/2`
(a probe, **not evidence**), the share of ticks on which a net-zero group
executed was:

| Policy | null-action rate | `O95`, registered menu | `O95`, strict menu |
|---|---|---|---|
| control-random | 0.062 | 0.000 | 0.125 |
| EBU-hostile | 0.146 | 0.333 | 0.271 |
| EBU-random | 0.208 | 0.771 | 0.729 |
| EBU-aligned | **0.417** | 1.000 | 1.000 |

The aligned arm parks on the null action in roughly two ticks in five.

The full rehearsal — 192 runs of 2048 ticks across both menu rules, three loads
and eight mechanically derived seeds — puts numbers on it
(**REHEARSAL / NON-CONFIRMATORY**). Median null-action rate and median `O95`:

| load | policy | null rate | `O95` registered menu | `O95` strict menu |
|---|---|---|---|---|
| `1/4` | control | 14.6% | 0.0085 | 0.0117 |
| `1/4` | hostile | 9.0% | 0.0000 | 0.0000 |
| `1/4` | EBU-random | 13.7% | 0.1156 | 0.1097 |
| `1/4` | aligned | **75.5%** | 1.0000 | 1.0000 |
| `1/2` | EBU-random | 13.7% | 0.0905 | 0.0736 |
| `1/2` | aligned | **50.8%** | 1.0000 | 1.0000 |
| `1` | EBU-random | 13.8% | 0.0661 | 0.0495 |
| `1` | aligned | 0.0% | 1.0000 | 1.0000 |

Two things follow. **The loophole is heavily used** — the aligned arm spends
three quarters of its ticks on a null action at the mildest load, falling to
zero at the heaviest where a real reversal always scores higher. **But it does
not change any qualitative conclusion**: removing net-zero groups lowers
EBU-random's occupancy modestly (0.116 to 0.110, 0.091 to 0.074, 0.066 to
0.050) and leaves every arm ordering intact. The aligned arm holds `O95 = 1`
either way, for the separate structural reason proved in
`ENDPOINT_SATURATION_FINDING.md`.

So the decision below is not about rescuing a result. It is about whether the
registered world should contain a costless null action at all.

### 3.2 It contradicts a stated property of Capacity V1

`gaussian_harness/capacity.py` states of the V1 rule: *"There is no borrowing,
arbitrary issuance, periodic refill, global pool, genesis grant or direct
capacity transfer between owners."*

Corollary N1.2 exhibits a direct capacity transfer between owners, at zero EBU
cost and with no physical effect. The accounting is exact and no invariant is
violated — `sum_a R_a = E_G = 0`, and `V + sum_i B_i = J` still closes exactly —
so this is not an accounting bug. It is a property of the mechanism that the
mechanism's own documentation says is absent. The docstring's claim is about
*primitive operations*; the transfer is *emergent* from group valuation plus
`owner(a) = src(a)`. Both readings are defensible, and the discrepancy is
recorded here rather than resolved by editing the docstring.

This channel is potentially consequential for a red-team arm: an EBU-hostile
actor can use inert groups to move capacity into whichever cell it next wants
to spend from, funding destruction it could not otherwise afford.

## 4. Scope: this is the registered Stage-A and Stage-B world

The same 21-group menu, the same `owner(a) = src(a)` rule and the same
valuation produced Stage A and Stage B. Net-zero groups were in both.

**Nothing in the registered record is invalidated.** Stage A and Stage B
measured what the declared world does, and this *is* the declared world. Their
artifacts, preregistrations, analyses and reports stand unchanged.

Two consequences are worth recording, and are labelled as what they are:

- **Fact.** The Stage-A and Stage-B random arms selected a net-zero group
  whenever the uniform draw landed on one of the three, so some fraction of
  their "executed" ticks moved no physical state.
- **Conjecture, untested.** The costless transfer channel of Corollary N1.2 may
  contribute to the capacity dynamics Stage B observed, by redistributing
  balances toward cells that are above reference. This has not been measured,
  is not required to explain the Stage-B finding, and no claim rests on it.

## 5. The decision the mission cannot take for the author

Mission section 6 says the mandatory-action rule *"is central to the scientific
interpretation"*, and section 33 makes a conflict between mandatory-action
semantics and physical-demand authority a stop condition. The question is
scientific, not technical:

> **Does the core four-policy comparison run on the registered 21-group menu,
> which contains a costless null action, or on an 18-group menu restricted to
> groups that actually change the physical state?**

Both are implemented and declared, neither is default-by-accident:

- `MENU_WITH_NET_ZERO` — the registered Stage-A/Stage-B menu, currently the
  code default so nothing changes silently.
- `MENU_STRICT_PHYSICAL` — the same menu with the three net-zero groups
  removed structurally, before any policy sees them.

Under either setting `null_action` is recorded per tick, so the rate is
measurable rather than assumed.

The trade-off is genuine. Keeping them preserves exact comparability with the
registered Stage-B world and keeps the action space physically honest — two
opposite transfers *are* a thing an actor can do. Removing them makes
"mandatory action" bite as section 6 intends, at the cost of running the
comparison in a world that is not quite the registered one, and of deleting a
physically realizable action because it is inconvenient.

**No preregistration is frozen until this is answered.** Everything that does
not depend on the answer has been completed under both settings.
