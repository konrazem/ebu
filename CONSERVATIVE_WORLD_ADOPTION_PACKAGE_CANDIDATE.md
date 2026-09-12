# Conservative World Adoption Package — Candidate

**Status: PROSPECTIVE ADOPTION PACKAGE CANDIDATE — not adopted; not a
scientific preregistration; not an implementation authorization; not an
execution authorization; not an SD-stage registration; not a book-programme
integration.**

**No scientific execution occurred.** No model, world, tick, transition loop,
viability-kernel computation, trajectory, parameter search, optimizer,
benchmark, test suite, runner, or simulation was executed. No SD-01, SD-03,
Gate 1E, AWS, Docker, SSO, or publication action occurred. No outcome was
inspected. The only computation performed was reading, static parsing, and
SHA-256 hashing of files already committed.

**No existing file was modified by this package.** This document and its
companion review `CONSERVATIVE_WORLD_ADOPTION_PACKAGE_REVIEW.md` are additive;
they are the only files created.

The working tree separately carries **pre-existing uncommitted user work** —
modifications to `EBU_FUTURE_BOOKS_STRUCTURE.md`,
`V3.0_LONG_HORIZON_NORMALIZED_MECHANISM_CANDIDATE.md`,
`V3.0_LONG_HORIZON_STUDY_DECISION_PACKET.md`, `longhorizon_v30.py` and
`test_v30_longhorizon.py`, plus an untracked
`V3.0_LONG_HORIZON_COST_AND_LAUNCH_PLAN.md`. **None of that was made here and
none of it was touched**; each was verified byte-identical before and after.
Because one of those paths is cited below, every line-number citation in this
package resolves against **HEAD**, not the working tree — see §K.

**Predecessor.** This package operationalises
`CONSERVATIVE_WORLD_FOUNDATION_DESIGN.md` (committed at `0726ccd`), whose
status and limits are binding here. Where that memo says something is not
established, this package does not establish it either.

---

## A. Plain-language decision page

### A.1 What this is

You are being asked to make **one** decision: whether to adopt a small,
fixed-topology, block-partitioned conservative token world as the physical
substrate for future EBU controller validation — or not.

Everything else in this package exists to make that decision informed. Nothing
in this package makes it.

### A.2 The recommendation, in plain English

**Recommended: a small ring of sites, updated in non-overlapping pairs, where
the resource is a whole number of indistinguishable "tokens" that can move
between named containers but can never be created or destroyed.**

Each site holds tokens in three named states: *accessible* (usable now),
*latent* (present but not yet usable), and *degraded* (used, awaiting
recovery). Each actor is a lasting individual with its own buffer of tokens and
its own demand. Tokens cycle: latent becomes accessible, accessible is drawn
and consumed into degraded, degraded slowly returns to latent. Every one of
those movements takes tokens out of one named container and puts the same
number into another.

The world updates by splitting the ring into non-overlapping pairs of adjacent
sites and updating each pair independently, alternating which pairs are used on
odd and even ticks.

### A.3 Why this is preferable

**Conservation becomes a finite check instead of a proof.** Because pairs never
overlap within a tick, the total is just the sum over pairs. If every entry in
the pair-update table moves tokens without changing the pair's total, the whole
world's total cannot change. You verify a table; you do not prove a theorem
about a global rule.

**It supports the three things a controller experiment needs.** Sites can have
different parameters. Actors persist and have identity. And — the point most
easily missed — there is a genuine *choice* at each step. A classical cellular
automaton has none of these: its rule is uniform, its cells are positions
rather than individuals, and its next state is a function of the current state
alone with no action to choose. A controller experiment needs `F(state, action,
demand)`, not `F(state)`.

**It removes joint-action ambiguity by construction.** If actors are placed at
least two sites apart, no pair ever contains two actors, so no two decisions
ever interact within a tick. There is nothing to allocate, nothing to settle,
and no interaction term — not deferred, but structurally absent.

**Regeneration cannot cheat.** There is no growth term that creates resource.
The **total** accessible stock across the world rises only by moving tokens out
of the latent reservoir, which falls by exactly the same integer. (Transport
moves accessible tokens between sites, so a *single* site's accessible stock can
rise without mobilisation; the world-wide total cannot.)

### A.4 The serious fallback

**An ordinary number-conserving cellular automaton on the same fixed ring**,
where conservation is checked after the fact using the published decision
procedure rather than guaranteed by the pair structure.

This is a real option, not a straw man. The number-conserving cellular-automaton
literature is the oldest and most developed body of theory among the families
compared — a judgement carried over from the predecessor memo's §3.1, where the
sources are given; no source is re-cited here. What it costs is that per-site
parameters, actor identity and the control input all have to be re-introduced
by encoding them into cell values, which is where specification ambiguity
historically enters.

### A.5 What you are being asked to decide

**You are being asked to decide only:**

1. which world family (if any) becomes the substrate;
2. whether the proposed conservation profile in §B is the right declaration of
   what is conserved and in what sense, including its **account level** (§B
   field 2 offers two, and they are not equivalent);
3. the **safe-set declaration** required by §C.11 — whether unmet demand is
   compatible with safety. §C.8.1 and §C.11.3 show why this matters and what
   depends on it;
4. whether a future implementation plan may be prepared.

The **information pattern** (§E.3) is *not* a decision: Form D is required for
the first world, and §H.1 records it as an acknowledgement rather than a
choice.

**You are NOT being asked to decide, and this package does not ask you to
approve:**

- any numerical scientific parameter value;
- any regime, horizon, demand schedule, or initial state;
- whether to write code;
- whether to run anything;
- any relationship between this world's token count and any EBU quantity;
- any account, permission, or settlement rule;
- any SD-stage registration or book placement.

### A.6 What remains impossible until a later authority exists

| Impossible now | Why | What would unblock it |
|---|---|---|
| Connecting this world to EBU in any way | The finite EBU quote law is recorded as a **candidate design**, not an acceptance; and no registered quantity relates tokens to EBU units | Acceptance of the quote law, plus the §F items |
| Testing "a viable action existed but permission blocked it" | No account, wallet, balance, permission or settlement layer exists anywhere in this repository, by design | Registered account/permission semantics. (`O3` and `O8` are separately open — §F.9, §F.10 — and are *not* registered as the account-layer blocker) |
| Calling this SD-01, or any SD stage | It is a different model class and a different question, on a different lineage | A separate registration or amendment — not this package |
| Claiming conservation has been verified | No transition table has been adopted, instantiated, enumerated, or verified | Adoption (§H), then an implementation authorization for the §D.1 checker, then the §D.1 check |
| Claiming either viability set is known | Neither `Inv(K₀)` nor `V_∞` has been computed | Adoption, then §D.1, then the separately authorized §D.2 and §D.3 steps (§D.2 lists "D.1 passed" as a required frozen input) |

### A.7 The decision, selectable

Exactly one of the following. **None is marked adopted. None is pre-selected.**

```
[ ]  OPTION 1 — Adopt the recommended family.
     A fixed-topology, block-partitioned conservative token world with
     integer token accounting, explicit internal reservoirs, and persistent
     actor identities, as specified symbolically in §C, under the
     conservation profile proposed in §B.

[ ]  OPTION 2 — Adopt the fallback family.
     An ordinary (non-partitioned) number-conserving cellular automaton on
     the same fixed ring, with conservation established by the published
     decision procedure rather than by block construction. §C would then
     require restatement, because per-site parameters, actor identity and
     the control input must be re-encoded.

[ ]  OPTION 3 — Decline adoption.
     Neither family is adopted. Name the family to be investigated instead:

     ______________________________________________________________

     A new comparison memo would be required before any further step.
```

---

## B. Proposed conservation profile

Field list taken verbatim from §14.2 of
`CONSERVATION_AND_BOUNDARY_ACCOUNTING_FOUNDATION.md`, which enumerates what a
declared boundary/conservation profile must contain "at least". That section is
explicitly gated: "If separately authorized, I-3 may add an optional declared
boundary/conservation profile containing at least:".

> **This package does not exercise the I-3 authorization and does not request
> it.** The field list is reused here only because reinventing a field list the
> repository has already written would be worse. Reusing the *shape* of a gated
> profile is not the same as adding one, and nothing below is offered as an I-3
> profile.

### B.0 The account level is itself a decision

`CONSERVATION_AND_BOUNDARY_ACCOUNTING_FOUNDATION.md` §3 defines three levels.
Two are candidates for `W0`, and the package deliberately does **not** pick:

| Option | Foundation's definition | Fits `W0` because | Does not fit because |
|---|---|---|---|
| **Level 1** — reduced represented-stock account | permitted claim: "The declared stock ledger closes, or its residual has a stated value"; **not** permitted: that any physical carrier is conserved | `Q` is an abstract token count, not a physical carrier — exactly the case Level 1 exists for | It does not express that `W0` declares **no boundary channel at all**; Level 1 is silent about closure |
| **Level 3** — isolated boundary-complete physical conservation | permitted claim: "The declared **physical** quantity is conserved in the isolated model under the stated assumptions" | `W0` really is isolated for `Q`: `B φ[k] = 0` identically, and the state contains every form `Q` can take | Its permitted claim is about a **physical** quantity. §3.3 warns that "A coordinate described only as useful stock, reserve, service capacity, burden, or EBU is not automatically a complete physical carrier coordinate" — and §B.1 denies `Q` is a physical carrier |

> **The honest summary:** `W0` has Level 3's *structure* with Level 1's
> *epistemic standing*. The foundation does not define a cell for that
> combination. The author should choose, and the choice should be recorded in
> §H.1 rather than assumed here.
>
> This package's own preference, offered as a preference and not as a finding:
> **Level 1, with the closure recorded as a declared model property rather than
> as a Level 3 certification.** Level 1's permitted claim is exactly what `W0`
> can support, and claiming Level 3 for a non-physical carrier invites precisely
> the misreading §3.3 warns against.

| # | Field (§14.2) | Proposed value | Source / rationale | Author acceptance required? | Required before implementation? |
|---|---|---|---|:--:|:--:|
| 1 | profile identifier and version | `CONSERVATIVE-WORLD-W0-PROFILE`, version `0.1.0-candidate` | New identifier; no existing profile covers a closed token world | **Yes** | **Yes** |
| 2 | account level | **AUTHOR CHOICE — two defensible readings, see §B.0** | The foundation's Level 3 is defined over *physical* carriers, and §B.1 denies `Q` is one; its Level 1 is defined for exactly a declared reduced stock ledger. Neither is a clean fit and the difference is not cosmetic | **Yes** | **Yes** |
| 3 | boundary identifier and hierarchy | Single boundary `W0-OUTER`. No child boundaries in the first world. No roll-up. | The first world is one flat closed region; the foundation's §8 roll-up rules are therefore not exercised | **Yes** | **Yes** |
| 4 | quantity identifier and units | Quantity `Q`; unit **`token`**. One carrier, one unit, no conversion anywhere in the model | An abstract carrier chosen precisely so that no physical identification is implied | **Yes** | **Yes** |
| 5 | state coordinates included in \(c_Q\) | `{acc_i, lat_i, deg_i}` for every site `i ∈ Z_N`, and `{buf_a}` for every actor `a`. Coefficient **1** on every one; no coordinate excluded; no coordinate weighted | §C.3. Capacity `κ_i`, reserve floor `R_i`, buffer floor `β_a` and all potential parameters are **constants, not coordinates**, and are **not** in `c_Q` | **Yes** | **Yes** |
| 6 | internal transformation map or declared invariant | The declared invariant is `c_Q^T S̃ = 0` — every transition column sums to zero. Operationally: **every entry of the adopted block table must have equal token sums before and after** (§C.8) | The foundation's §4 condition, restated as a finite table condition by the block structure | **Yes** | **Yes** |
| 7 | boundary-flow channels and sign convention | **NONE.** `B φ[k] = 0` identically. The channel list is declared **empty**, not merely unused | A closed first world. Any future boundary channel is a profile amendment, not a runtime option | **Yes** | **Yes** |
| 8 | observability status | **Fully observed.** The state is the model's own integer state. No measurement model, no sensor, no estimation, no uncertainty model | There is nothing to observe imperfectly: the model *is* its own **physical-conservation** ledger — ledger 1 of the five the foundation's §9 requires to stay separate. It is **not** the represented-stock, EBU-accounting, causal-attribution, or institutional-settlement ledger | **Yes** | **Yes** |
| 9 | exact or uncertainty-aware residual policy | **Exact integer equality:** \(Q_{\mathrm{post}}-Q_{\mathrm{pre}}=0\). **No tolerance, absolute or relative.** A non-zero residual is a **refusal**, never a tolerance case and never a scientific outcome | The foundation's §4.3 forbids a hidden or universal tolerance and requires a named policy. Integer state makes exactness available, so anything weaker would be a choice to be less rigorous than the substrate allows | **Yes** | **Yes** |
| 10 | explicit nonclaims about isolation and completeness | See §B.1 | Required by §14.2, whose tenth field is "explicit nonclaims about isolation and completeness"; modelled on (not required by) the foundation's own §19 nonclaims list | **Yes** | **Yes** |

### B.1 Explicit non-claims attached to this profile

The profile does **not** claim, and acceptance of it would not claim, that:

- `Q` is energy, mass, charge, matter, or any physical carrier;
- the world is physically realistic, physically complete, or a model of
  anything outside itself;
- Level 3 here certifies physical completeness — it records that *within the
  declared model* nothing crosses the boundary, because the model declares no
  boundary channel;
- the closure of `Q` establishes homeostasis, stability, viability,
  efficiency, or good behaviour of any kind. The foundation's §11 supplies the
  standing counterexample: "a lossless two-state system can conserve a sum
  while deviations grow in opposite directions. Conservation alone does not
  prove Lyapunov stability.";
- `Q` is, relates to, or bounds any EBU quantity (§F). The foundation's §9
  lists five ledgers that must remain separate and warns that "no scalar
  should silently serve all five roles"; `Q` serves **one** of them — physical
  conservation — and no other;
- this profile is accepted, Level 3 certified, or physically complete.

### B.2 What acceptance of the profile would and would not settle

Acceptance would settle *what is being conserved and in what sense*. It would
**not** settle any transition table, any parameter, any initial state, or any
relationship to EBU.

---

## C. Complete symbolic W0 specification

> **A transition table has not been adopted, instantiated, enumerated, or
> verified.**

This section is implementation-ready in *form* and deliberately empty of
*values*. It contains **no numeric tuples of any kind, illustrative or
otherwise**. Every symbol below is a declared free parameter whose value is
fixed at a later, separately authorized stage.

### C.1 Topology — fixed

- `N ∈ 2ℤ`, `N ≥ 4`: the number of sites. Fixed for the life of the world.
- Sites indexed `i ∈ Z_N`, arranged in a ring; site `i` is adjacent to
  `i−1` and `i+1` modulo `N`.
- **No site is ever added, removed, activated, refined, merged, or rewired.**
  Growth and topology change are out of scope (§G.3).

### C.2 Block partition — alternating, non-overlapping

```
P_even = { {0,1}, {2,3}, …, {N−2, N−1} }
P_odd  = { {1,2}, {3,4}, …, {N−1, 0} }

P(t) = P_even   if t ≡ 0 (mod 2)
P(t) = P_odd    if t ≡ 1 (mod 2)
```

Each `P(t)` is a partition of `Z_N` into exactly `N/2` disjoint adjacent pairs.
**Every site belongs to exactly one block at every tick.** Two sites share a
block at some tick if and only if they are adjacent.

### C.3 Token coordinates — the complete state

Per site `i ∈ Z_N`, three integer coordinates:

| Coordinate | Meaning |
|---|---|
| `acc_i ∈ ℤ≥0` | accessible stock — drawable this tick |
| `lat_i ∈ ℤ≥0` | latent stock — present, not drawable until mobilised |
| `deg_i ∈ ℤ≥0` | degraded stock — consumed, awaiting recovery |

Per actor `a ∈ {1, …, A}`, one integer coordinate:

| Coordinate | Meaning |
|---|---|
| `buf_a ∈ ℤ≥0` | the actor's own held tokens |

> **`buf_a` is not an account.** It is a physical token coordinate inside
> `c_Q` with coefficient 1, conserved like every other, and structurally the
> same kind of object as the site reserve floor `R_i`. It carries **no** credit,
> debit, price, balance, affordability or permission semantics. It gates nothing
> but physical feasibility and the declared homeostatic floor. It is the nearest
> thing in `W0` to an account and **must never be read as one** (§E.5, §F.8).

The token configuration is `s = ((acc_i, lat_i, deg_i)_{i∈Z_N}, (buf_a)_{a})`,
a vector of `3N + A` non-negative integers. **These `3N + A` coordinates are
exactly the coordinates in `c_Q`, each with coefficient 1, and there are no
others.**

### C.4 Declared constants — not state, not in `c_Q`

Per site `i`:

| Constant | Meaning |
|---|---|
| `κ_i ∈ ℤ≥0` | accessible-stock capacity: `acc_i ≤ κ_i` |
| `R_i ∈ ℤ≥0` | reserve floor on accessible stock, `R_i ≤ κ_i` |
| `m_i(·) : state → ℤ≥0` | mobilisation rate cap (may read only site-`i` coordinates) |
| `ψ_i(·) : state → ℤ≥0` | recovery rate cap (may read only site-`i` coordinates) |
| `(α_i, β^{pot}_i, χ_i, L_i, U_i, R^{pot}_i, K^{pot}_i)` | the seven parameters carried by `d0_v29.LocalView` alongside the state `x` — `alpha, beta, chi, L, U, R, K` — **carried but not read by `W0`** (§C.12) |

Per block-adjacent pair `{i,j}`:

| Constant | Meaning |
|---|---|
| `c_{ij} ∈ ℤ≥0` | per-tick transport capacity across that pair |

Per actor `a`:

| Constant | Meaning |
|---|---|
| `h(a) ∈ Z_N` | home site. Fixed. |
| `β_a ∈ ℤ≥0` | buffer floor |
| `ν_a ∈ ℤ≥0` | per-tick draw cap |
| `d_a(·)` | demand schedule (§C.10) |

> **Notation note.** `W0`'s capacity is written `κ_i` and its reserve floor
> `R_i` to avoid collision with the safe set `K` (§C.11) and with `d0_v29`'s own
> `K` and `R`. The `d0_v29` parameters are listed separately above and are
> superscripted `pot` where the names would otherwise clash. **No `d0_v29`
> parameter is read by any `W0` transition.** Two further collisions are noted
> rather than renamed, because `W0` never reads the `d0_v29` side: `W0`'s
> capacity `κ_i` is unrelated to `d0_v29.Cell.kappa` (a proportional leak), and
> `W0`'s actor count `A` is unrelated to `d0_v29.Cell.A` (the Allee threshold).

> **Which `d0_v29` type, and why the difference matters.** The seven-parameter
> set above is what `d0_v29.LocalView` carries alongside the state `x`
> (`d0_v29.py:172–182`). It is **not** the full `d0_v29.Cell`, which declares
> **fourteen** fields (`d0_v29.py:70–94`): those seven plus `s`, `d`, `lam`,
> `kappa`, `source`, `rho`, `A`.
>
> Those seven extra fields are the external-inflow, demand, leak and
> **regeneration** machinery — `source` takes values `none | finite | logistic |
> allee`, and `rho` is the regeneration rate. They are exactly the
> non-conservative drive that `W0` excludes by construction (§C.8). **`W0`
> adopts neither `Cell` nor its drive term**; it borrows only the seven
> potential parameters, and even those it does not read.

### C.5 Actor placement rule

> **Placement constraint.** For every pair of distinct actors `a ≠ b`, the ring
> distance between `h(a)` and `h(b)` is `≥ 2`.

Consequence, by C.2: since two sites share a block only when adjacent, **no
block ever contains two actors, at any tick, under either partition.** Each
block therefore hosts at most one decision. The constraint requires
`A ≤ ⌊N/2⌋` and is checkable by inspection of the placement alone.

### C.6 Time, phase, and the augmented state

Ticks `t ∈ ℤ≥0`. The partition has period 2. Let each actor `a` have a declared
demand period `p_a ∈ ℤ≥1` (§C.10). Define

```
L = lcm(2, p_1, p_2, …, p_A)
φ(t) = t mod L
```

The **augmented state** is `s⁺ = (s, φ)` with `φ ∈ Z_L`.

> **Per-actor periods, not one shared period.** Actors may carry different
> periods. `L` must be the least common multiple of `2` and **every** `p_a`;
> using a single actor's period, or omitting the factor `2` for the partition,
> would make the phase wrong and the viability computation invalid. With `A = 1`
> this reduces to `L = lcm(2, p_1)`. `L` must be recorded at adoption, because
> `|S⁺| = |S| · L` and therefore the whole enumeration budget depends on it.

> The transition law depends on tick parity *and* on demand phase. Viability
> must therefore be computed on the augmented space `S⁺ = S × Z_L`, or it is
> not well-defined. Computing it on `S` alone would be an error.

### C.7 The conserved quantity and legal states

\[
Q=\sum_{i \in Z_N}\left(\mathrm{acc}_i+\mathrm{lat}_i+\mathrm{deg}_i\right)
+\sum_{a=1}^{A}\mathrm{buf}_a .
\]

A configuration is **legal** iff all of:

1. every coordinate is a non-negative integer;
2. `acc_i ≤ κ_i` for every site `i`;
3. `Q(s) = Q₀`, the declared total, for the world's whole life.

> **Finiteness, which condition 3 alone supplies.** Conditions 1 and 2 bound
> `acc_i` but leave `lat_i` and `deg_i` individually unbounded. Finiteness comes
> from condition 3: since every coordinate is non-negative and all `3N + A` of
> them sum to `Q₀`, each is at most `Q₀`, so the legal set is contained in a
> finite box and `|S| ≤ C(Q₀ + 3N + A − 1, 3N + A − 1)`, with capacity caps
> reducing it further. `|S⁺| = |S| · L`. **This argument must be recorded at
> adoption**, because without condition 3 the state space is infinite and the
> exact methods of §D.2 and §D.3 do not apply at all.

Legality is a property of the *state space*. It is **not** the safe set: a legal
state may be unsafe (§C.11).

### C.8 Transition families, the control input, and legality

Every transition moves tokens between named coordinates. Each family below is
**block-internal**: every coordinate it touches is owned by a single block of
`P(t)`.

> **Naming.** Three-letter family names are used deliberately. The single
> letters `C`, `V`, `M`, `D`, `J`, `f`, `S` are **reserved** for the EBU process
> cost `C_a`, the local potential `V_loc` and the viability sets `V_k`/`V_∞`,
> edge mobility `M_e`, the demand set `D(φ)`, the flux `J_e`, the force `f_e`,
> and the incidence `S_e`. **No `W0` transition family reuses any of them.** An
> earlier draft named consumption `C_a(u)`, colliding exactly with the EBU cost
> term that §F.4 exists to keep separate; the collision is removed here.

| Family | Effect | Per-family cap | Selected by |
|---|---|---|---|
| Mobilisation `MOB_i(g)` | `lat_i −= g`, `acc_i += g` | `0 ≤ g ≤ min(lat_i, m_i(s), κ_i − acc_i)` | **autonomous rule** |
| Recovery `REC_i(r)` | `deg_i −= r`, `lat_i += r` | `0 ≤ r ≤ min(deg_i, ψ_i(s))` | **autonomous rule** |
| Transport `TRN_{i→j}(q)` | `acc_i −= q`, `acc_j += q` | `0 ≤ q ≤ min(acc_i, c_{ij}, κ_j − acc_j)`, `{i,j} ∈ P(t)` | **autonomous rule** |
| Consumption `CON_a(u)` | `buf_a −= u`, `deg_{h(a)} += u` | `u = min(d_a(t), buf_a)` — **an equality, not a bound** | **mandatory** |
| Draw `DRW_a(w)` | `acc_{h(a)} −= w`, `buf_a += w` | `0 ≤ w ≤ min(acc_{h(a)}, ν_a)` | **the control input** |

**No creation and no destruction.** Every family removes an integer from one
named coordinate and adds the same integer to another. There is no growth term,
no logistic term, no source, and no sink. The **world-wide total** accessible
stock `Σ_i acc_i` can rise only by mobilisation, which debits `Σ_i lat_i` by
exactly the same integer; transport redistributes accessible tokens between
sites without changing that total.

#### C.8.1 Why consumption is mandatory — and what goes wrong if it is not

> **Consumption is an equality, not a bound.** At every tick each actor moves
> `u_a = min(d_a(t), buf_a)` from `buf_a` to `deg_{h(a)}`. This is metabolism:
> it is not chosen, not refusable, and not capped by a controller.

This is not a stylistic choice. Without at least one mandatory transition the
world has no dynamics of its own, and the consequence is fatal to the entire
purpose of the package:

> **Degeneracy result (why §D.3 would otherwise be vacuous).** Suppose every
> family had lower bound `0`, so that the all-zero block action ("do nothing")
> were always available, and suppose the safe set `K` were a predicate on the
> state alone. Then the no-op's successor *is* the current state, so from any
> `s ∈ K` the no-op keeps the state in `K` forever. The stationary all-no-op
> policy would then witness `K⁺ ⊆ V_∞`, and `V_∞ ⊆ V_0 = K⁺` by construction, so
>
> ```
> V_∞ = K⁺   exactly,   with the §E.2 recursion stabilising at k = 1.
> ```
>
> The viability oracle would certify every legal safe state, distinguish
> nothing, and be answerable by inspection without executing anything. §E.4
> category 1 would coincide with `s ∉ K` and be unreachable from a legal start.
> The four failure mechanisms the package is built to study would all be
> *elective*: a policy could only lose viability by choosing to.

Mandatory consumption removes the degeneracy: standing still drains `buf_a` at
rate `d_a(t)` until it falls below `β_a` and the state leaves `K`. The actor
must therefore draw; drawing requires accessible stock at its home site;
replenishing that site requires mobilisation from a finite `lat`, or transport
that only occurs when the site is co-blocked with its neighbour; and the tokens
consumed reach `deg`, returning to `lat` only at rate `ψ_i`. Those four
constraints are what make the decision problem non-trivial.

> **What is still open, and must not be assumed.** Mandatory consumption makes
> `V_∞ ⊊ K⁺` *possible*. It does **not** establish that the resulting world is
> **decision-sensitive** — that some policies survive and others do not. The
> world could still turn out trivially survivable, or trivially doomed, for
> some or all parameter choices. **Which of the three it is, is exactly what
> §D.2 and §D.3 would determine, and this package establishes none of it.**

#### C.8.2 The autonomous rule, and what the controller actually chooses

The block action is the tuple

```
A_B = ( g_i, g_j, r_i, r_j, q_{i→j}, q_{j→i}, u_a, w_a )
```

where `u_a` and `w_a` are present only if some actor `a` has `h(a) ∈ B` — at
most one such actor, by §C.5 — and absent otherwise.

Its components are **not** all choices:

- `g_i, g_j, r_i, r_j, q_{i→j}, q_{j→i}` are fixed by a **declared deterministic
  autonomous rule**, a function of the frozen block pre-state alone. They are
  physics, not decisions.
- `u_a` is fixed by the mandatory equality above.
- **`w_a` is the only control input in `W0`.**

> **This must be declared at adoption, and it is why World A is well defined.**
> Deleting the actors (World A, §D.2) removes `u_a` and `w_a` and leaves only
> autonomous components, so World A is a deterministic **map** `F(s)`, every
> forward orbit is eventually periodic, and "the orbit's eventual period" is a
> well-formed output. Had the mobilisation, recovery and transport amounts
> remained free, World A would have been a nondeterministic transition
> *relation* with no orbits at all, and `Inv(K₀)` would silently have become
> *controlled* invariance — the very object §D.2 insists it is not.

Declaring the autonomous rule is a required part of adoption (§H.1). This
package does not select it: any deterministic function of the frozen block
pre-state, respecting the per-family caps and the composed legality condition
below, is admissible.

> **A second reason to restrict the control input.** Because a block may contain
> one actor and one non-actor site, a tuple in which the actor chose
> `g_j, r_j, q` would let that actor control its *neighbour's* physics — and
> which actor controls a given site would flip with the partition parity.
> Restricting the control input to `w_a` removes that artefact.

#### C.8.3 Composed legality — the per-family caps are necessary, not sufficient

> **This is a normative condition on the tuple, not on its components.**

The components are applied **simultaneously** against one frozen pre-state, but
each per-family cap is a *unilateral* bound read off that same snapshot.
Unilateral bounds on a shared coordinate do not compose. Two counterexamples,
each built only from cap-satisfying components:

| | Setup | Components, each within its own cap | Composed result |
|---|---|---|---|
| **Capacity breach** | `κ_i = 5`, `acc_i = 0`, `lat_i = 5`, `m_i = 5`, `acc_j = 5`, `c_{ij} = 5` | `g_i = 5 ≤ min(5,5,5)` ✓ and `q_{j→i} = 5 ≤ min(5,5,5)` ✓ | `acc_i' = 0 + 5 + 5 = 10 > κ_i` ✗ |
| **Negativity breach** | `h(a) = i`, `acc_i = 5`, `ν_a = 5`, `c_{ij} = 5`, ample headroom at `j` | `w_a = 5 ≤ min(5,5)` ✓ and `q_{i→j} = 5 ≤ min(5,5,·)` ✓ | `acc_i' = 5 − 5 − 5 = −5 < 0` ✗ |

**In both cases `Q` is still exactly conserved** — the tokens were only moved —
so a check that looks only at `ΔQ_B` reports clean while the successor is
illegal. Worse, the obvious defensive reflex, clamping `acc_i` into `[0, κ_i]`,
**creates or destroys exactly the excess tokens** and is the one way this design
can actually break conservation.

Every adopted table entry must therefore satisfy, for its composed successor:

```
acc_i' = acc_i + g_i + q_{j→i} − q_{i→j} − w_a·[h(a)=i]     0 ≤ acc_i' ≤ κ_i
lat_i' = lat_i − g_i + r_i                                   lat_i' ≥ 0
deg_i' = deg_i − r_i + u_a·[h(a)=i]                          deg_i' ≥ 0
buf_a' = buf_a + w_a − u_a                                   buf_a' ≥ 0
```

and symmetrically for `j`.

> **Clamping is forbidden.** An entry whose composed successor is illegal is
> **rejected**, never repaired. The `residual` field of §C.14 is computed on the
> **unclamped** successor. A table containing such an entry fails §D.1.

Additionally, `min(q_{i→j}, q_{j→i}) = 0` is required — a simultaneous two-way
transport is a distinct action from the no-op with identical net effect, and it
makes `c_{ij}` ambiguous between a per-direction and a per-pair bound. With the
constraint, `c_{ij}` bounds net flow across the pair.

#### C.8.4 The block-table condition and the format of the table

> **Block-table condition.** Let `Q_B` be the sum of all token coordinates owned
> by block `B`. Every entry of the adopted table must satisfy
> `Q_B(after) = Q_B(before)` exactly, over the integers. Because `P(t)`
> partitions the coordinate set, `Q = Σ_{B ∈ P(t)} Q_B`, so the table condition
> gives `ΔQ = 0` globally.

The adopted table's **format must be declared**, because it determines whether
that condition has any content:

| Format | `ΔQ_B = 0` | What §D.1 must therefore check |
|---|---|---|
| **Family-tuple** — each entry is a tuple of the five families above | **Automatic.** Each family is by definition a pair of equal and opposite increments, so no tuple can violate it | **Composed legality** (§C.8.3). `ΔQ_B = 0` is *recorded*, not *tested* |
| **Raw map** — each entry is an explicit pre-state → post-state pair | **Not automatic.** An entry can be written that violates it | Both `ΔQ_B = 0` **and** composed legality, plus block-internality and `c_Q`-membership |

**This package recommends the family-tuple format**, and recommends that §D.1
be labelled honestly for it: under that format §D.1 verifies *legality*, and
conservation is a property of the format rather than a test result. Choosing
the raw-map format instead is admissible and makes §D.1 a genuine conservation
test; the choice belongs to adoption.

An adopted table must additionally be **total**: for every legal block
pre-state the admissible set is non-empty. Note that the no-op is *not*
available as a universal fallback, because consumption is mandatory (§C.9).

### C.9 The no-op, and why it is not a universal fallback

> **Definition.** The **no-op** for block `B` is the block action whose *control
> input* is zero: `w_a = 0`. It is **not** an action in which nothing happens.
> The autonomous components `g, r, q` still take the values their declared rule
> assigns, and `u_a = min(d_a(t), buf_a)` is still consumed.

Properties:

1. The no-op is **always available as a choice** — `w = 0` satisfies
   `0 ≤ w ≤ min(acc_{h(a)}, ν_a)` for any pre-state. The *physically feasible*
   control set is therefore never empty.
2. The no-op **does not leave the state unchanged**. Consumption is mandatory,
   so `buf_a` falls by `min(d_a(t), buf_a)` every tick under the no-op.
3. The no-op is therefore **not** always homeostatically admissible. Repeated
   no-ops drive `buf_a` below `β_a` in at most `⌈(buf_a − β_a + 1)/d_a⌉` ticks
   whenever `d_a(t) > 0`, at which point the state has left `K`.
4. A state can accordingly have a non-empty *physically feasible* control set
   and an **empty admissible set** — when every available `w` leads out of `K`.
   That is exactly the condition that makes a state non-viable, and it is
   reachable from inside `K`.

> **Why this matters, and what would go wrong without mandatory consumption.**
> Under a purely optional action set and a state-only `K`, property 2 fails: the
> no-op's successor would be the current state, so the no-op would pass the §C.13
> step-5 screen from *every* state in `K`, the admissible set could never be
> empty inside `K`, one-step screening could never certify non-viability, and
> §C.14's `empty_admissible_set` receipt field could never fire from a safe
> state. §C.8.1 shows the same defect at the fixpoint level. Property 2 is what
> repairs both.

> **One-step screening must stay one-step.** §C.13 step 5 screens a candidate by
> whether its *immediate* successor lies in `K`. It must **not** consult `V_∞`
> or any multi-step reachability property: `A_adm` is an input to the §E.2
> recursion that defines `V_∞`, so letting `A_adm` depend on `V_∞` would be
> circular. Multi-step reasoning belongs to the oracle, never to the screen.

### C.10 Demand schedule interface

A demand schedule is a declared function

```
d_a : ℤ≥0 → ℤ≥0       for each actor a
```

subject to:

- **deterministic** — no seed, no draw, no stochastic rule;
- **periodic** with a declared per-actor period `p_a`, so that
  `L = lcm(2, p_1, …, p_A)` is finite and `S⁺` is finite;
- **preregistered** — written down in full before any computation that could
  reveal an outcome.

> **The first world uses no stochastic demand.** This is not a preference; a
> non-periodic or random schedule makes `S⁺` infinite or unenumerable and
> destroys the exactness that is the entire reason for this substrate.

Richer demand (bursts, shocks, seasonality, correlation) is a later extension
requiring its own authority and its own re-derivation of `L`.

### C.11 Homeostasis / safe-set interface

```
K₀ = { s : ∀i,  acc_i ≥ R_i }                             (no actors)
K  = { s : ∀i,  acc_i ≥ R_i   ∧   ∀a,  buf_a ≥ β_a }      (with actors)
K⁺ = K × Z_L                                              (augmented)
```

`K₀`, `K` and `K⁺` are **declared constraint sets**, fixed before any result is
seen.

> **The capacity ceiling is deliberately absent from `K`.** `acc_i ≤ κ_i` is a
> **legality** condition (§C.7 clause 2) satisfied by every legal state, so
> repeating it inside `K` would do no work and would make §C.13's `screen_reason`
> ambiguous between the physical screen 5(a) and the homeostatic screen 5(b).
> Capacity violations are always reported as **physical**-screen rejections.

#### C.11.1 Well-posedness of the declaration

A declaration is **ill-posed**, and must be rejected at adoption rather than
discovered later, unless

```
Σ_i R_i  +  Σ_a β_a   ≤   Q₀
```

and the per-site floors are simultaneously satisfiable under the capacity caps,
i.e. `R_i ≤ κ_i` for every `i`. Without this, `K = ∅` by arithmetic and every
later step is wasted. **This is a static check available at §D.1 time**, not a
discovery to be made after a §D.3 execution authorization.

#### C.11.2 The one-tick draw-to-consume latency

Because §C.13 step 1 freezes the pre-state and consumption is capped by `buf_a`
read from it, **an actor cannot consume tokens it draws in the same tick**:

```
buf_a(t+1) = buf_a(t) + w_a − min(d_a(t), buf_a(t))
```

So a draw made at tick `t` is only available for consumption at `t+1`. This is a
substantive dynamical property, not a bookkeeping detail: it means the actor
must anticipate demand by at least one tick, and it interacts directly with the
declaration below.

#### C.11.3 The safe-set declaration required at adoption

The declaration must state **which of these two** is the safe condition:

| Option | `K` | Consequence |
|---|---|---|
| **(i) Rationing permitted** | as written above — a floor on `buf_a`, no service requirement | Unmet demand does not by itself leave `K`. The actor may serve less than `d_a(t)` and remain safe as long as its buffer holds. |
| **(ii) Demand must be met** | `K` additionally requires `buf_a ≥ d_a(φ)` at the pre-state, so that the mandatory consumption is `u_a = d_a(t)` in full | Combined with §C.11.2, `K` effectively becomes `K ∩ {buf_a ≥ max(β_a, d_a(φ))}`, and `K` becomes **phase-dependent**. Any state with `buf_a(t) < d_a(t)` is unsafe no matter what action is taken, because drawing cannot rescue it within the tick. |

> **This is not a matter of degree.** Option (ii) makes `K` depend on `φ`, which
> changes the shape of the whole viability computation; option (i) keeps `K`
> state-only. Both are viable *given mandatory consumption* (§C.8.1) — it is
> mandatory consumption, not the choice between (i) and (ii), that rescues the
> oracle from the degeneracy. But the two give different kernels, and the choice
> must be recorded in §H.1 before anything is computed, never selected after
> seeing a result.

### C.12 Coordinates not used by `W0`

The seven `d0_v29` per-cell parameters are carried in the site declaration but
**no `W0` transition reads them**. They exist solely so that a future EBU layer,
if ever authorized, would have a declared place to read from. Carrying them
asserts nothing about whether they are the right parameters, and §F.2 records
that *which* `W0` coordinates would enter `V_loc` is unregistered.

### C.13 Exact update order

Per tick `t`, in exactly this order:

| Step | Action |
|---|---|
| 1 | **Freeze** the complete pre-state `s(t)`. Every later computation this tick reads only `s(t)`. No live-state update. |
| 2 | **Select** the partition `P(t)` by tick parity, and the phase `φ(t)`. |
| 3 | **Evaluate** demand `d_a(t)` for every actor. Deterministic. |
| 4 | **Generate** the candidate block-action set per block from the adopted block table (§C.8). The menu is a function of the frozen block pre-state and the demand — **never randomly generated, never hand-supplied**. |
| 5 | **Screen** each candidate for (a) physical feasibility (§C.8 caps, non-negativity, capacity) and (b) homeostatic admissibility against `K` (§C.11). *Screened-out actions are removed here and can never be re-admitted later in the tick.* |
| 6 | *(Not present in `W0`, World A, World B, or World C.)* A future controller would evaluate its value **only on the actions surviving step 5**, then apply account permission. **No such controller and no such permission layer exists (§F).** |
| 7 | **Select** exactly one action per block. The selector is **the declared autonomous rule** for `g, r, q`, **the mandatory equality** for `u_a`, and **the policy or controller** for the single control input `w_a` (§C.8.2). For a block containing no actor the action is fully determined by the autonomous rule. |
| 8 | **Apply** all block maps against the frozen `s(t)`. Blocks are disjoint, so the outcome is independent of the order in which they are applied. |
| 9 | **Record** the receipt (§C.14), including the conservation residual. |

> **Step 5 strictly precedes step 6, with no exception.** A large controller
> value must never make a physically or homeostatically inadmissible action
> selectable. This ordering mirrors the constraint the repository already
> enforces, where P1C "remains the physical permission layer" and the quote
> module "receives q_acc and quotes only [0, q_acc]"
> (`ebu_quote_v30.py:24–26`), and where falsifier **F5** is "a positive quote
> bypasses P1C" (`v30_quote_validation_plan.json`).

### C.14 Receipt / evidence fields

Every tick must emit a receipt carrying at least:

| Field | Purpose |
|---|---|
| `tick`, `parity`, `phase` | position in time and in the partition/demand cycle |
| `pre_state_digest` | canonical digest of the frozen `s(t)` |
| `partition` | the block list actually used |
| `demand_vector` | `d_a(t)` for every actor |
| `candidate_set_digest`, `candidate_set_size` | per block, what was generated at step 4 |
| `admissible_set_digest`, `admissible_set_size` | per block, what survived step 5 |
| `screen_reason` | per rejected candidate, which screen removed it |
| `selected_action` | per block |
| `post_state_digest` | canonical digest of `s(t+1)` |
| `Q_pre`, `Q_post`, `residual` | **`residual` must be exactly `0`**; any other value is a refusal |
| `empty_admissible_set` | boolean, per block — a visible viability failure, not a crash |

Fields reserved for **later, separately authorized** stages, and absent from
`W0`: any oracle verdict, any controller value, any account balance, any
permission decision, any settlement line.

---

## D. Verification plan before any controller exists

Each step below is a **future** step. None has been performed.

> **Classification matters.** Step D.1 is *static verification*: it checks
> arithmetic on a declared table without advancing any world state. Steps D.2,
> D.3 and D.4 **apply the transition function and are therefore model
> execution**, even though they touch no scientific hypothesis. Under
> `AGENTS.md` — "do not call step functions, runners, simulations, or
> trajectories, even for one tick" when execution is not authorized — each of
> them requires its own execution authorization. Calling them "just
> verification" would be exactly the disguise `AGENTS.md` forbids.

### D.1 Finite block-table conservation enumeration

| | |
|---|---|
| **Kind** | **Static verification.** No world state advances. |
| **Inputs that must already be frozen** | the adopted block table; the coordinate list of `c_Q`; the residual policy (§B field 9) |
| **Exact output** | for every table entry: `Q_B(before)`, `Q_B(after)`, their difference, **and the composed successor with its legality verdict** (§C.8.3) |
| **Pass** | every entry has difference exactly `0` **and** a legal composed successor |
| **Fail** | any entry has a non-zero difference, **or** a composed successor violating `0 ≤ acc' ≤ κ`, `lat' ≥ 0`, `deg' ≥ 0`, or `buf' ≥ 0` |
| **Refusal** | the table is incomplete, non-total, references a coordinate outside `c_Q`, is not block-internal, contains a clamped successor, or has an undeclared format (§C.8.4) |
| **Establishes** | that the adopted table satisfies the block-table condition **and** that every entry's composed successor is legal, hence that `ΔQ = 0` for every legal tick and that the state space stays finite |
| **Note on content** | Under the recommended family-tuple format, `ΔQ_B = 0` is **automatic** and is recorded rather than tested; the substantive test is composed legality. Under a raw-map format both are genuine tests. §C.8.4 requires the format to be declared, precisely so that this row is not vacuous |
| **Does NOT establish** | anything about trajectories, viability, homeostasis, stability, or physical meaning |

### D.2 Autonomous World A invariant-set calculation

| | |
|---|---|
| **Kind** | **Model execution** (autonomous; no actors, no controller) |
| **Inputs that must already be frozen** | D.1 passed; `N`; `κ_i`, `R_i`, `m_i`, `ψ_i`, `c_{ij}`; `Q₀`; `K₀`; and **the declared deterministic autonomous rule** (§C.8.2), without which World A is a transition *relation* rather than a map and the output below is not well-formed |
| **Exact output** | `Inv(K₀)` — the maximal forward-invariant subset of `K₀ × Z_L` — plus, for each state, its orbit's eventual period |
| **Pass** | `Inv(K₀) ≠ ∅` **and** the declared initial family lies inside it |
| **Fail** | `Inv(K₀) = ∅`, or the declared initial family lies outside it |
| **Refusal** | the enumeration exceeds a declared state or time budget → `COMPUTATIONALLY_INCONCLUSIVE`, never a silent truncation or a sampled substitute |
| **Establishes** | that the world does not leave its own constraint set under its own dynamics — i.e. that a later collapse cannot be blamed on badly chosen physics |
| **Does NOT establish** | anything about actors, demand, controllers, or EBU. Invariance here is *uncontrolled* invariance; it is a different object from the controlled invariance of D.3 |

> **World A is not currently passed. `Inv(K₀)` has not been computed.**

### D.3 World C exact finite viability kernel

| | |
|---|---|
| **Kind** | **Model execution** (exhaustive, controlled) |
| **Inputs that must already be frozen** | D.1 passed; D.2 evaluated; `A`, `h(a)`, `β_a`, `ν_a`; the demand schedule and every period `p_a`, hence `L`; `K`; **the information pattern (§E.2)**; the full controlled block table |
| **Exact output** | `V_∞ ⊆ K⁺`, the greatest fixpoint; the iteration count to stabilisation; and, for every `s⁺ ∈ V_∞`, the set of actions preserving membership |
| **Pass** | `V_∞ ≠ ∅` **and** the declared initial family lies inside it |
| **Fail** | `V_∞ = ∅`, or the declared initial family lies outside it |
| **Refusal** | budget exceeded → `COMPUTATIONALLY_INCONCLUSIVE`; or the declared information pattern does not match the pattern a later controller would actually face (§E.3) |
| **Establishes** | that survival is possible from the declared start, independently of any controller — and *which* actions preserve it |
| **Does NOT establish** | that any particular policy achieves it; that the world is interesting; or anything whatsoever about EBU |

> **World C is not currently passed. `V_∞` has not been computed.**

### D.4 Transparent World B non-EBU policy comparison

| | |
|---|---|
| **Kind** | **Model execution** (trajectories) |
| **Inputs that must already be frozen** | D.3 completed with `V_∞ ≠ ∅`; the declared non-EBU policy; the horizon |
| **Exact output** | the trajectory; the first tick (if any) at which the policy leaves `V_∞`; and which structural mechanism was responsible — distribution, transport bottleneck, reserve depletion, or degradation lock-up |
| **Pass / Fail** | **Neither. This step has no pass condition.** Both "the policy leaves viability" and "the policy never leaves viability" are results and must be reported as found |
| **Refusal** | budget exceeded, or the policy is modified after its behaviour is observed |
| **Establishes** | whether a transparent policy without lookahead can leave a viability kernel that is known to be non-empty, and by what mechanism |
| **Does NOT establish** | that any controller would do better; that the policy is optimal or bad; anything about EBU |

> **Do not optimise or degrade the comparison policy.** If it never loses
> viability, that is the finding. Altering the world afterwards to manufacture a
> collapse is the specific failure this whole programme is built to prevent.

### D.5 EBU smoke test — separately authorized, currently blocked

| | |
|---|---|
| **Kind** | **Model execution plus an EBU evaluation** |
| **Inputs that must already be frozen** | D.1–D.4 complete; **and every item in §F that blocks an EBU step** |
| **Status** | **BLOCKED.** Not authorized by this package and not authorizable by it |
| **Note** | A one- or two-tick smoke test is still a model execution, and is still an EBU evaluation. Neither is made harmless by being short |

---

## E. Viability oracle contract

### E.1 What the oracle is and is not

The oracle answers exactly one question per augmented state:

> *Does at least one admissible action policy preserve the declared homeostasis
> condition over the stated horizon?*

It does **not** rank actions, value them, score them, or carry an objective. It
is not a competitor to any controller and must never be used as one. It is a
membership test plus a witness set.

### E.2 The recursion, and the three information patterns

On the finite augmented space `S⁺ = S × Z_L`, with `A_adm(s⁺, d)` the set
surviving §C.13 step 5:

**Form D — deterministic declared demand (the first world).**
`d_a(t)` is a declared deterministic function, so `D(φ)` is a singleton `{d(φ)}`
and the recursion is

```
V₀      = K⁺
V_{k+1} = { s⁺ ∈ V_k : ∃ a ∈ A_adm(s⁺, d(φ)), F(s⁺, a, d(φ)) ∈ V_k }
```

**Form A — demand revealed BEFORE the action** (discriminating kernel):

```
V_{k+1} = { s⁺ ∈ V_k : ∀ d ∈ D(φ), ∃ a ∈ A_adm(s⁺, d), F(s⁺, a, d) ∈ V_k }
```

**Form B — action committed BEFORE demand** (minimax / target-tube). Note that
`A_adm(s⁺)` carries no `d` argument here; if the adopted `K` is phase-dependent
(§C.11.3 option (ii)) then `A_adm` depends on `d`, and Form B must be read with
`A_adm(s⁺) := ⋂_{d ∈ D(φ)} A_adm(s⁺, d)`. This is non-binding while Form D is
mandated, and becomes live the moment §E.3 is relaxed:

```
V_{k+1} = { s⁺ ∈ V_k : ∃ a ∈ A_adm(s⁺), ∀ d ∈ D(φ), F(s⁺, a, d) ∈ V_k }
```

Always **`V^B_∞ ⊆ V^A_∞`**, because `∃a ∀d φ ⟹ ∀d ∃a φ` pointwise and both
operators are monotone from the same `V_0 = K⁺`. Equality holds under an
Isaacs-type saddle condition — a standard result, cited for orientation and not
established here. Under Form D the distinction collapses, because with
`D(φ) = {d(φ)}` a singleton, both `∀d ∃a` and `∃a ∀d` reduce to the same
statement `∃a. F(s⁺, a, d(φ)) ∈ V_k`.

**Termination.** `S⁺` is finite and `V_{k+1} ⊆ V_k` by construction, so the
chain stabilises in at most `|K⁺|` steps at a fixpoint `V_∞`, the maximal
controlled-invariant subset of `K⁺`. Finiteness is what makes this true: in the
continuous case the limit of the same recursion need not be the maximal set
without a compactness assumption.

### E.3 Required information-pattern discipline

> **The first world must use Form D with a deterministic preregistered demand
> schedule.** This is a requirement, not a default.

Form D removes the information-order ambiguity entirely: with a singleton
disturbance set there is no order to get wrong, so the oracle cannot be
optimistic relative to the controller's information.

> **The trap this avoids.** If demand ever becomes uncertain and Form A is used
> while the real controller must commit *before* demand is revealed, the oracle
> certifies states the controller cannot actually hold. It would then
> misattribute the resulting failure to the controller (category 2 below) when
> the truth is category 1. **An optimistic information pattern must never be
> allowed to certify a controller that commits before demand is known.** Any
> future move away from Form D must declare the pattern explicitly and justify
> that it matches the controller's actual information.

### E.4 Currently meaningful diagnostic categories

For a future decision at augmented state `s⁺`:

| # | Condition | Reading |
|---|---|---|
| **1** | `s⁺ ∉ V_∞` | **Physically impossible from here.** The world was already lost. A failure here must **not** be attributed to the controller. |
| **2** | `s⁺ ∈ V_∞`, a viability-preserving admissible action existed, and the controller selected an action leaving `V_∞` | **The controller chose a non-viable action.** A genuine controller failure. |
| **3** | `s⁺ ∈ V_∞` and the controller's selection stays in `V_∞` | **The controller preserved viability** under the declared conditions. |

Per-decision record required to separate these: membership of `s⁺` in `V_∞`;
the candidate set; the admissible set; the subset of admissible actions
preserving `V_∞`; and the selection.

### E.5 The fourth category, and why it is not testable

A fourth category — **"a viable admissible action existed, but the account or
permission layer forbade every one of them"** — is scientifically important and
is **not testable**.

No EBU account, wallet, balance, permission, or settlement layer exists in this
repository. `p1c_v29.py:19` records that P1C "implements NO ecological debt, NO
EBU, NO wallet, NO scalarisation, NO restoration credit, NO
resource-conversion price"; `V3.0_LOCAL_EBU_FOUNDATION_DRAFT.md:5` records that
the foundation "implements nothing: no EBU engine, no wallet, no market, no
exchange, no actor economy"; and `v30_o14_multi_edge_plan.json:194` records
that "cumulative signed EBU is an evaluation variable, not a wallet". `O3` and
`O8` are open.

**This category must not be simulated, approximated, or stood in for by a
penalty, a weight, or a soft constraint.** Until account semantics are
registered, the honest scope of any future experiment is categories 1–3 only,
and that limitation must be stated in its results.

---

## F. EBU bridge gate

> **Nothing in this section is filled in.** No equation, unit, conversion,
> surrogate score, wallet, penalty, weight, or allocation rule is proposed
> here. Where something is missing it is recorded as missing.

Blocking columns: **[N]** non-EBU `W0` verification (§D.1–D.4); **[R]** an
EBU *ranking-only* smoke test; **[M]** any magnitude, settlement, or account
claim.

| # | Requirement | Current status | [N] | [R] | [M] |
|---|---|---|:--:|:--:|:--:|
| F.1 | **Acceptance of the finite EBU quote law** `Δe(q) = V_loc(z) − V_loc(z + dt·S_e·q) − C_a(q)` | **CANDIDATE DESIGN, NOT ACCEPTED.** `V3.0_LOCAL_EBU_FOUNDATION_DRAFT.md:1141` lists it under "Candidate designs (not adopted as truth)" as "the object Gate 1 must validate and attack" | no | **BLOCKS** | **BLOCKS** |
| F.2 | **Which `W0` coordinates enter `V_loc`** | **UNREGISTERED.** `V_loc` is built from `v_i(x) = α[L−x]₊² + β[x−U]₊² + χ[R−x]₊²` (`d0_v29.py:188–194`) over a single reduced-stock coordinate. `W0` has four kinds (`acc`, `lat`, `deg`, `buf`). Which enter, and with which parameters, nothing declares | no | **BLOCKS** | **BLOCKS** |
| F.3 | **`potential-unit` → `EBU-unit` identification** | **MISSING.** SD-03 prerequisite **P5**: the chain "ends in an 'EBU-unit' that nothing defines in terms of the potential" | no | **BLOCKS** — see §F.3a | **BLOCKS** |
| F.4 | **`C_a` for `W0` actions** | **DECLARATION REQUIRED.** The `ProcessCost` type exists with `C(0)=0`, `C ≥ 0`; which process burdens `W0`'s five transition families carry is undeclared. Any declaration must satisfy the Gate-1A.1 no-double-count restriction — `C_a` prices only the category whose registered literal is `ALLOWED_COST_CATEGORY = "unrepresented_action_process_burden"`, never a burden already inside the `V_loc` difference (`ebu_quote_v30.py:56–68`) | no | **BLOCKS** | **BLOCKS** |
| F.5 | **`f_e = μ_i − η_e μ_j`** | **UNREGISTERED.** SD-03's configuration declares "no edge, no threshold `theta_e`, no mobility `M_e` and no efficiency `eta_e`" (`SD_03_PRE_EXECUTION_READINESS.md` §4), and its status there is **REFUSED**, which is an absence of registration, not a judgment of applicability. *Author's observation, not a registered determination:* `W0`'s transport is lossless integer with degradation as a separate typed transition, so the two-endpoint lossy form would not obviously describe it even if it were registered | no | no — the endpoint difference does not require it | **BLOCKS** any claim about the generator chain |
| F.6 | **`J_e = M_e[f_e − θ_e]₊`** | **MISSING.** Requires `M_e`, `θ_e`, which nothing declares for such a world. **No registered relation exists between `J_e` and `W0`'s integer transport quantity `q_{i→j}`, and none may be assumed** — the observation that the Onsager form is real-valued while `q` is integral is an author's observation about a mapping that does not exist, not a registered determination | no | no | **BLOCKS** any claim about the generator chain |
| F.7 | **`Ψ_e`** | **MISSING.** Unregistered, and its derivation "is itself registered as pending future Part I work under separate authority" (`SD_03_PRE_EXECUTION_READINESS.md` §4) | no | no | **BLOCKS** any claim about the generator chain |
| F.8 | **Account, permission, settlement semantics** | **DOES NOT EXIST, BY DESIGN.** See §E.5 | no | no — a ranking-only test selects without an account, but then cannot claim any permission result | **BLOCKS**, and blocks diagnostic category 4 entirely |
| F.9 | **`O3` — aggregate multi-edge quote / allocation** | **OPEN.** `v30_o14_multi_edge_plan.json:140`: "aggregate multi-edge quote/allocation - REMAINS OPEN; no settling aggregate arm is registered" | no — `W0` has no joint action at all (§C.5) | no | **BLOCKS** any joint or allocated value |
| F.10 | **`O8` — overexecution settlement** | **OPEN.** `ebu_quote_v30.py:28`: "full settlement semantics are OPEN (O8)" | no | no | **BLOCKS** any settlement |

### F.3a Why an unregistered identification blocks even a ranking

An earlier draft of this package asserted that "a ranking is invariant under any
strictly increasing identification, so ordering survives". **That is false as
stated, and the correction matters because it was the single sentence making an
EBU step look partly reachable.**

The object being ranked is not a potential *level*. It is

```
Δe(q) = V_loc(z) − V_loc(z + dt·S_e·q) − C_a(q)
```

— a **difference** of potentials, minus a cost. Whether a monotone
identification `φ` preserves the ranking depends on *where `φ` is applied*, and
**nothing registers that**:

| Where `φ` is applied | Ranking preserved? |
|---|---|
| To the **final** `Δe` value | Yes, for any strictly increasing `φ` — trivially, since ranking is by that value |
| To the **potential values**, before differencing | **No**, in general |

Counterexample for the second reading, with `φ(x) = x³` (strictly increasing on
ℝ) and both actions evaluated at `V_loc(z) = 0`:

| Action | `V_loc(z′)` | `C_a` | `Δe` under identity | `Δe` under `φ` |
|---|---:|---:|---:|---:|
| 1 | `−1` | `1/2` | **`1/2`** | `1 − 1/8` = **`7/8`** |
| 2 | `−2` | `19/10` | **`1/10`** | `8 − 6859/1000` = **`1141/1000`** |

Identity ranks action 1 above action 2; `φ` reverses it. (Exact rational
arithmetic; no model was executed.)

The invariance class that actually works is a **positive scaling**
`φ(x) = c·x`, `c > 0`, applied **uniformly to `V_loc` and `C_a`**. A
positive-affine `φ(x) = cx + k` preserves the potential difference alone,
because the offset cancels, but breaks once `C_a` is not scaled by the same `c`.

Since **P5 leaves both the identification and its point of application
unregistered**, neither reading may be assumed, and the ranking cannot be relied
on. F.3 therefore blocks a ranking-only smoke test unless a positive-scale
identification is separately declared *and* its point of application is fixed.

> **Inherited.** `CONSERVATIVE_WORLD_FOUNDATION_DESIGN.md` carries the same
> incorrect sentence. That memo is committed and is **not** edited by this
> package; the defect is recorded here and in §K and in the companion review.

### F.1a Summary of the gate

- **Non-EBU `W0` verification (§D.1–D.4) is blocked by nothing in this table.**
  That is the substantive finding: the entire viability programme — conservation
  check, World A, World C, World B — can be specified and later carried out with
  the EBU bridge untouched.
- **An EBU ranking-only smoke test is blocked by F.1, F.2, F.3 and F.4.**
  F.3 is not closed by monotonicity alone (§F.3a).
- **Any magnitude, settlement or account claim is blocked by F.1–F.4 and
  F.8–F.10**; and F.5–F.7 additionally block any claim about the generator
  chain.

### F.1b What must not be done to close this gate

No item above may be closed by: inventing an equation; inferring a unit;
substituting a per-unit value, reward, weighted sum, penalty, or surrogate
objective; introducing a wallet; adopting an allocation rule; or treating a
diagnostic as a settlement. `Q` is a token count. It is **not** EBU, and
nothing in this package proposes that it is.

---

## G. Programme and books boundary

**No programme or book document is altered by this package.**

### G.1 What this substrate is not

| Claim | Status |
|---|---|
| It is SD-01 | **No.** `W0` is a closed multi-reservoir integer world; SD-01 is an **open control volume**. See §G.1a for the provenance of that claim. Different model class, different question, and on a lineage this branch does not carry as an operative local authority. |
| It satisfies an SD-01 prerequisite | **No.** |
| It satisfies SD-03 | **No.** SD-03 validates the finite EBU chain. `W0` contains no EBU chain and does not touch SD-03's prerequisites `P1`–`P7`. |
| It satisfies SD-05 | **No.** SD-05 measures multi-action interaction. `W0` has no joint action at all (§C.5), so it contains no interaction quantity to measure. |
| It satisfies SD-06 | **No.** SD-06 requires a subset lattice to invert. `W0` has one action per block and no subset table. |
| It is registered, adopted, or preregistered | **No.** |

### G.1a Provenance of the SD-01 conservation-class claim

This claim needs its provenance stated explicitly, because it **cannot be found
by grepping this checkout** and two independent reviewers of this package
concluded from that absence that the identifier was fabricated. It is not.

| | |
|---|---|
| Source | `stage_d_scientific_validation_master_matrix.json`, the canonical Stage D matrix |
| Where it lives | **the git object store only** — blob `e6cd44f8b9e2e125403cb1359d819fc08afd2cb7`. The path is **not** in this branch's tree or working tree; the SD programme lineage split from this branch and has not rejoined |
| Integrity | size `148183` bytes; SHA-256 `081f2e994c23051514aef19a0516d1996d9c4b86cd528dfc05bf9d17658bdb81` — recomputed for this package and matching |
| How to reproduce | `git cat-file -p e6cd44f8b9e2e125403cb1359d819fc08afd2cb7`, then read `studies[]` where `study_id == "SD-01"` |
| Field | `conservation_accounting.class` = `"OPEN_CONTROL_VOLUME"` |
| Corroborating field | `model_domain.boundary` = `"open control volume; every declared shock and external replenishment is a boundary exchange"` |
| Corroborating field | `model_domain.model` = `"one-stock regenerative resource with explicit demand, loss, reserve, shock, and policy ledgers"` |

> **A grep of the working tree returns nothing for `OPEN_CONTROL_VOLUME`, and
> that is expected.** Absence from this checkout is not absence from the
> repository. The matrix is read here **read-only from the object store**, under
> digest verification, solely to avoid inventing what the programme already
> registers — and it is **not** treated as an operative local authority on this
> branch.

### G.2 What it may later support

A **separately registered** study could use this substrate. That would require
its own registration or amendment, its own frozen question, its own controls
and falsifiers. This package neither performs nor requests that registration.

### G.3 Possible conceptual homes, both requiring separate authority

- **Part V's constrained state transition and viable-set material** — the books
  register's Part V chapter V.3 already states that "an isolated extension must
  debit regeneration from an internal reservoir"
  (`EBU_FUTURE_BOOKS_STRUCTURE.md:364`), which is structurally what §C.8's
  mobilisation family does. **That is a resemblance, not a placement**, and it
  confers no book slot; V.3 is a planned chapter, not an authority this package
  may occupy.
- **The future boundary/conservation profile** — §14.2 of
  `CONSERVATION_AND_BOUNDARY_ACCOUNTING_FOUNDATION.md`, which
  `EBU_FUTURE_BOOKS_STRUCTURE.md` gates behind "a later, separate I-3
  authorization" (HEAD line 982 — see §K on line-number stability).

**Neither home is claimed, occupied, or requested here.** Growth, topology
rewriting, refinement, and recursive reuse remain out of scope for the first
world and are not part of this decision.

---

## H. Author action and stop conditions

### H.1 Approval template

```
CONSERVATIVE WORLD — ADOPTION DECISION

Decision (select exactly one):

  [ ] OPTION 1 — adopt the recommended block-partitioned fixed-topology
                 token-world family (§A.7, §C)
  [ ] OPTION 2 — adopt the ordinary number-conserving CA fallback (§A.7)
  [ ] OPTION 3 — decline; investigate instead: ______________________

Conservation profile (§B):

  [ ] accepted as proposed
  [ ] accepted with the amendments recorded below
  [ ] not accepted

  Amendments: ______________________________________________________

Account level (§B.0, §B field 2 — select exactly one):

  [ ] Level 1 — reduced represented-stock account   (this package's preference)
  [ ] Level 3 — isolated, within the declared model only

Safe-set declaration required by §C.11.3 (select exactly one):

  [ ] (i)  rationing permitted — unmet demand does not by itself leave K
  [ ] (ii) demand must be met every tick to remain in K  (makes K phase-dependent)

Future implementation plan (§A.5 item 4):

  [ ] a future implementation plan may be prepared (a document, not code)
  [ ] not yet

Acknowledgement, not a choice (§E.3):

  [ ] I understand that Form D — deterministic preregistered demand — is
      REQUIRED for the first world, and that Forms A and B are unavailable
      until a later authority relaxes it.

Authorized by: ____________________   Date: ______________
```

### H.2 What acceptance would authorize

Acceptance of this package would authorize **exactly three things and nothing
else**:

1. **choosing a world family**;
2. **declaring a conservation profile**;
3. **preparing a future implementation plan** — a document, not code.

### H.3 What acceptance would explicitly NOT authorize

| Not authorized | Later authority required first |
|---|---|
| Selecting numerical scientific regimes, parameters, horizons, or initial states | A preregistration fixing the regime and its justification **before** any outcome is visible, under the `AGENTS.md` rule against post-outcome tuning |
| Writing code — **including the §D.1 static checker** | An implementation authorization naming the exact files and their scope. §D.1 needs no *execution* authorization because it advances no world state, but it still needs code, and writing code is not authorized here |
| Running tests | A test authorization; and note that a test that advances model state is model execution, not testing |
| Executing the model — including §D.2, §D.3, §D.4, and including a single tick | A separate execution authorization per rung, per `AGENTS.md`'s execution-safety rule |
| Any EBU mapping | Acceptance of the quote law (F.1) plus F.2 and F.4; F.3 for magnitudes |
| Account, permission, or settlement semantics | Registered account authority; `O3` and `O8` closed |
| SD-stage registration | A separate registration or amendment on the programme lineage |
| Book integration | A separate books-programme authorization; and for the conservation profile specifically, the I-3 authorization gated at `EBU_FUTURE_BOOKS_STRUCTURE.md` HEAD line 982 |
| AWS, Docker, or any external resource | A separate operational authorization; no cost, host, or budget is proposed anywhere in this package |
| Publication | A separate publication authorization |

### H.4 Stop conditions

Work must stop, and this package must be revised rather than proceeded from,
if any of the following is true:

- the block table cannot be made total (some block pre-state has an empty
  candidate set even including the no-op);
- the §D.1 conservation enumeration fails on any entry;
- `Inv(K₀)` is empty, or the declared initial family lies outside it;
- `V_∞` is empty, or the declared initial family lies outside it;
- the finite state space exceeds the declared enumeration budget, in which case
  the correct outcome is `COMPUTATIONALLY_INCONCLUSIVE` — never a sampled,
  truncated, or approximated substitute;
- any step is tempted to close an §F gap by invention.

---

## I. Non-claims

This package does not claim, and acceptance of it would not claim, that:

- any world family has been adopted, implemented, instantiated, or executed;
- any transition table exists, has been enumerated, or has been verified;
- conservation has been verified for any concrete world;
- World A or World C has been passed, computed, or established;
- EBU has been validated, or that the quote law is accepted;
- any EBU unit, mapping, account, permission, or settlement rule exists;
- `Q` is, relates to, or bounds any EBU quantity;
- `Q` is energy, mass, or any physical carrier, or that the world is physically
  realistic or complete;
- this is SD-01, or satisfies any SD prerequisite;
- this is registered, preregistered, or integrated into any book;
- any scientific parameter has been selected;
- any scientific computation was performed in producing this package. **None
  was.**

---

## J. Authority boundary

> Before implementation, execution, book integration, or SD-stage
> registration, an explicit prospective authorization is required to (1) choose
> and adopt a world family, (2) define its conservation profile, and (3) define
> the relationship, if any, between the world's quantity `Q` and the EBU
> accounting quantity — including the explicit option of recording that there is
> **none**.
>
> This package **proposes** (1) and (2) for author decision and **declines** to
> propose (3), because §F records that the material required for it does not
> exist and must not be invented.

---

## K. Citation stability note

Line-number citations in this package resolve against **HEAD (`0726ccd`)**, not
against the working tree.

This matters because `EBU_FUTURE_BOOKS_STRUCTURE.md` is one of the protected
paths that is **modified and uncommitted** in the working tree. Its uncommitted
version carries roughly 95 additional lines, so a line number read from the
working tree does not resolve in any committed object:

| Quoted text | HEAD line | Working-tree line |
|---|---:|---:|
| "Under a later, separate I-3 authorization, the framework may add an optional…" | **982** | 1077 |
| Part V chapter V.3, "…an isolated extension must debit regeneration from an internal reservoir." | **364** | 364 |

The V.3 citation is stable because the uncommitted additions fall after it; the
I-3 citation is not.

> **Inherited defect, recorded rather than repaired.** The predecessor memo
> `CONSERVATIVE_WORLD_FOUNDATION_DESIGN.md` cites the I-3 sentence as
> `EBU_FUTURE_BOOKS_STRUCTURE.md:1077`, which is the **working-tree** line. At
> the commit that memo was committed in, the sentence is at line 982. The quoted
> text itself is verbatim and the substantive point is unaffected. **That memo is
> committed and is not edited by this package**; the defect is recorded here and
> in the companion review, and this package uses the HEAD line.

Citations into any protected, uncommitted path should be given as HEAD line
numbers or as section references, never as working-tree line numbers.
