# Independent audit response — Dynamic Scalar Capacity theorem

Scope: **Theorem DS / L1–L3 only.** The static demand-driven architecture and
all prior resolved defects were not reopened.

## VERDICT

```
RETURN FOR CORRECTION
```

The claimed necessary-and-sufficient characterization fails in the **necessity**
direction, and a **load-bearing hypothesis is missing** from the zero pattern.
Findings 5 and 6 below are independent additional gaps.

---

## Finding 1 (PRIMARY — missing hypothesis). Zero pattern

**Question asked.** What happens when the same allowed edge has `E_theta = 0`
under one field and `E_theta != 0` under another?

The defining relation is `s(e) = lambda_theta(e) E_theta(e)` with
`lambda_theta(e) in (0, infinity)`. On a **mixed** edge:

- under the field with `E_theta(e) = 0`: `s(e) = lambda * 0 = 0` for **every**
  finite `lambda`;
- under the field with `E_theta'(e) != 0`: `s(e) != 0`.

These cannot both hold. **No finite positive `lambda_theta(e)` exists**, so the
relation simply fails at that (edge, field) pair.

The report evades this by stating the requirement only "for every action edge of
**nonzero** EBU" and adopting the *weak reading*, under which a mixed edge is
classified **strict** and settles a nonzero amount. That exemption is
load-bearing and is **incompatible with R5, R8 and R9**:

> Freeze the world at the field where `E_theta(e) = 0`. Capacity V1 settles
> `Delta c = E_theta(e) = 0`. The mechanism settles `s(e) != 0`. No unit
> normalization `p` reconciles them, so **R5 fails at that frozen field**, and the
> settlement is not a positive multiple of the valuation in force, so **R8/R9
> fail** at that edge.

**Exact necessary condition (the answer to question 1):**

```
for every edge e and all fields theta, theta' :      E_theta(e) = 0  <=>  E_theta'(e) = 0
```

i.e. **the zero-set of `E` must be field-independent — no mixed edges.** This
must be added as hypothesis **Z**; it is not implied by L1–L3. (The report states
this as the "strong reading" and then does not adopt it.)

---

## Finding 2 (EXACT COUNTEREXAMPLE). L3 is not necessary

**Claim under audit:** existence holds *iff* L1 ∧ L2 ∧ L3, where L3 is
factor-additive representability, `W(x) = sum_F W_F(x_F)`.

**Counterexample.** Two declared factors, values `A in {a,b,c}`, `B in {p,q,r}`.
Six states, three allowed edges, **each edge changing both factors**:

```
(a,q) -> (b,p)        (b,r) -> (c,q)        (c,p) -> (a,r)
```

One field: `V(a,q)=1, V(b,p)=0, V(b,r)=1, V(c,q)=0, V(c,p)=1, V(a,r)=0`.

- **R4 imposes no restriction here.** Every action's touched support is the whole
  factor set, so a receipt may depend on both factors. **Any `W` is factor-local.**
- **A valid settlement potential exists:** `W := V` satisfies all three strict
  inequalities. L1 holds trivially (single field); L2 holds (acyclic).
- **No factor-additive `W` exists, for any real values.** Adding the first two
  constraints gives `A_a + B_r > A_c + B_p`, i.e. `W(a,r) > W(c,p)`, contradicting
  the third. *(Confirmed exhaustively over a `7^6` integer grid and closed
  algebraically.)*

**Therefore a valid, R4-compliant `W` exists while L3 fails, so L3 is sufficient
but NOT necessary, and the "iff" is false as stated.**

**What L3 must be replaced by.** The genuine R4 condition is graph-dependent:
for each action, the settlement difference must be invariant under variation of
spectator factors **that the action graph actually realizes**. Factor-additivity
implies that, but is strictly stronger on a sparse graph. Either replace L3 with
that condition, or declare an explicit richness hypothesis under which the two
coincide.

---

## Finding 3. L2 is redundant, not independent content

**L2 is implied by L1** and adds nothing.

*Proof.* Suppose the contracted strict digraph had a cycle
`x_1 ≻ y_1 ~ x_2 ≻ y_2 ~ ... ~ x_1`, where `~` denotes a universally-null path.
Choose a field `theta*` making the first edge strictly positive. Null paths give
`V_theta*(y_i) = V_theta*(x_{i+1})` (universally null means zero under every
field). Each strict edge gives `V_theta*(x_i) >= V_theta*(y_i)` — strict if
nonzero under `theta*`, equal otherwise, and never negative because L1 forbids a
sign flip. Chaining: `V_theta*(x_1) > V_theta*(x_2) >= ... >= V_theta*(x_1)`,
a contradiction. Likewise no strict edge can lie inside a contracted class, since
a null path forces `V_theta` equal at its endpoints for every field. ∎

*Confirmed exhaustively:* over all two-field families on a 4-path, a 4-ring, a
triangle and `K4` drawn from a declared value grid, **L1 held in 8,766 cases and
L2 failed in 0 of them**. And **L1 alone** matches the existence oracle
6561/6561, 6561/6561, 729/729.

The 13,851-case check in the report cannot detect this: criterion and oracle were
built from the same specification, so both reduce to L1.

**The minimal characterization is Z ∧ L1 (+ the corrected locality condition).**

---

## Finding 4. `W` is not canonical, and rival choices change decisions

**Question asked.** Does static-V1 recovery fix `W` up to positive scale and
additive constant?

**Only for a single-field family.** With one field, R5 forces `W = V_theta0` up to
positive affine. With two or more fields, L1 constrains only **adjacent** pairs;
non-adjacent pairs are free.

*Witness.* Edges `a≻b`, `c≻b`, `c≻d`; the pairs `(a,c)`, `(a,d)`, `(b,d)` are
non-adjacent. Both

```
W1 = (a:10, b:0, c:1,  d:1/2)        W2 = (a:1, b:0, c:10, d:1/2)
```

are valid and are **not** affinely related — they order `a` against `c`
oppositely.

**They change affordability.** With `c_0 = 0` at `x_0`, the balance after any path
to `x` is `W(x_0) - W(x)`, so the test `c + Delta c >= 0` reduces exactly to
`W(y) <= W(x_0)`. From `x_0 = a`: `W1` permits reaching `{a,b,c,d}`, `W2` permits
only `{a,b,d}`. **Same physics, same L1–L3, different admissible action sets.**

So Theorem DS is an **existence** result, not a determinate mechanism: the wallet
is underdetermined by the physics, and the residual choice is economically
consequential. That must be stated, and a canonicalization rule declared.

---

## Finding 5. Static recovery with simultaneous receipts is not established

Single actions: with `W := V_theta0` and `p = 1`, `Delta c = E` exactly — V1
recovered.

But per-owner **common-path receipts** require
`R_a = -∫_0^1 grad V(z + s delta_G)^T delta_a ds`, i.e. `W` defined and
differentiable **along the continuous path**. Theorem DS constructs `W` from a
**topological order on the vertices**; such a labelling has no canonical
continuous extension. **For a generic DS-constructed `W`, per-owner receipts are
undefined.**

Static recovery *including simultaneous per-owner receipts* therefore holds only
for the specific choice `W = V_theta0`, not for the class Theorem DS delivers.
The report's own hypothesis (PATH) is stated for R1/R2 but is not carried into
Theorem DS.

---

## Findings 6–8. Confirmed correct

| # | claim | verdict |
|---|---|---|
| 5 | `Delta c = W(before) - W(after)` gives exact aggregate no-minting on **all** allowed cycles, sparse graphs included | **CONFIRMED.** Telescoping is structural and indifferent to sparsity; 2,000 random closed walks on random sparse graphs gave circulation exactly zero in every case |
| 7 | one scalar nominal ruler exists only when all relevant local action values rescale by one common positive factor | **CONFIRMED.** `E_theta'(e_i)/E_theta(e_i) = q_theta'/q_theta` is forced to be edge-independent. One hypothesis must be made explicit: `Delta c_i != 0`, which is exactly hypothesis **Z** of Finding 1 |
| 8 | multiplying wallet and cost by the same positive factor leaves affordability unchanged | **CONFIRMED.** `q(c + Delta c) >= 0 ⟺ c + Delta c >= 0` for `q > 0`; zero violations over the tested grid. Only `q > 0` is needed |

---

## Required corrections

1. **Add hypothesis Z** (field-independent zero pattern) and withdraw the weak
   reading, which breaks R5/R8/R9 at mixed edges.
2. **Replace L3** with the graph-dependent spectator-invariance condition, or
   declare the richness hypothesis under which factor-additivity is necessary.
   As stated, the "iff" is false.
3. **Demote L2** to a remark; it is implied by L1.
4. **State that `W` is non-canonical** with ≥2 fields, and that rival choices
   change admissible action sets; declare a canonicalization rule.
5. **Carry (PATH) into Theorem DS**, or restrict the static-recovery claim with
   receipts to `W = V_theta0`.

Restated minimally, what survives is:

> **Z ∧ L1** is necessary and sufficient for a persistent scalar settlement
> coordinate on the allowed-transition graph; locality and canonicality are
> separate, and neither is delivered by L1–L3 as written.
