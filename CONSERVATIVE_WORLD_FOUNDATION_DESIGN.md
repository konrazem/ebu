# Conservative World Foundation — Design Memo

**Status: RESEARCH DESIGN MEMO — prospective comparison and recommendation
only. Not an adopted physical model; not an SD-01 registration; not an EBU-law
acceptance; not an execution authorization; not a book-programme integration.**

**No scientific execution occurred.** No model, tick, trajectory, simulation,
runner, parameter search, benchmark, test suite, Docker, AWS, or SSO action was
performed in producing this memo. No outcome was inspected. The only
computations performed were static combinatorics (binomial coefficients),
SHA-256 digests of files already committed, and reading.

**No existing file was modified.** This memo is additive. The long-horizon
candidate, the books register, the conservation foundation, every protocol,
every JSON plan, and all code and tests are unchanged.

---

## 0. How to read this memo

This memo compares candidate mathematical substrates for a future, small,
closed-accounting world in which a decision controller could later be tested
without the world itself being the confound. It recommends one family and one
fallback, specifies the recommended family formally enough to be criticised,
and then reports — without repair — every place where the recommended world
cannot yet be connected to this repository's EBU material.

Three reading rules apply throughout.

1. **Every external citation supports a narrow technical point and nothing
   else.** No source cited here mentions, evaluates, or validates EBU, this
   repository, or any controller-validation methodology. Where a citation could
   not be confirmed against a primary record it is marked `UNVERIFIED`. No
   theorem numbers are cited, because none were confirmed against published
   versions.
2. **Repository authority outranks external literature** on every EBU question.
   Literature is used only for the physical/mathematical substrate.
3. **Status language is load-bearing and is quoted, never paraphrased.** A
   draft is not an authority; a candidate is not an acceptance.

---

## 1. Executive decision

### 1.1 Recommendation

> **Recommended first world family:** a deliberately small, **fixed-topology,
> block-partitioned conservative cellular world** with **integer token
> accounting**, **explicit internal reservoirs**, and **persistent actor
> identities**.
>
> **Reason:** it is the only candidate in which exact conservation is a
> *finitely checkable property of a construction* rather than a property that
> must be proved about a global rule, while simultaneously admitting the three
> things a controller experiment requires and a classical cellular automaton
> does not have: heterogeneous per-cell parameters, persistent actor identity,
> and a genuine control input.

> **Serious fallback:** an **ordinary (non-partitioned) number-conserving
> cellular automaton** on the same fixed lattice, with conservation established
> after the fact by the published decision procedure rather than by
> construction. It is a real fallback, not a straw man; §4.2 states exactly what
> is lost.

### 1.2 Verdict table

| Determination | Verdict | Basis |
|---|---|---|
| Recommended base formalism | **block-partitioned conservative cellular world, integer tokens, fixed topology** | §4, §5 |
| Exact global conservation | **CONSTRUCTIBLE — not yet verified** | The construction makes conservation *finitely verifiable*: once a block table is adopted, checking that every entry has equal token sums before and after is a finite exact check, and the partition argument (§6.3) then gives global invariance. **No block table exists and none has been checked.** |
| Autonomous-world viability (World A) | **COMPUTABLE AFTER ADOPTION — not yet computed** | Once the autonomous transition table, the parameters and `K₀` are adopted, the maximal invariant subset of `K₀` can be obtained by exact orbit enumeration on a finite state space (§7). **Nothing has been enumerated.** |
| Actor-loaded viability (World C) | **COMPUTABLE AFTER ADOPTION — not yet computed** | Once the controlled transition relation, the safe set `K` and the information pattern (§9.2 form A or B) are adopted, the viability kernel is the greatest fixpoint of the controllable-predecessor operator and terminates on a finite state space (§9). **No kernel has been computed.** |
| Growth / topology (16 → 64) | **CONDITIONAL** | The substrate is compatible — activating a site with zero tokens preserves `Q` trivially — but growth is **out of scope for the first world** and needs its own authority (§13). |
| Recursive structure / refinement | **CONDITIONAL** | Splitting a site preserves the additive invariant by construction; *behavioural* equivalence does not follow and is exactly the open question, correctly deferred (§13.3). |
| EBU bridge | **BLOCKED** | Six named items are missing or unregistered, and the quote law itself is recorded as a candidate design, not an acceptance (§12). |
| **Overall** | **GO** to specify; **NO-GO FOR ADOPTION** | A family can be recommended and specified with **no new mathematics**. Adopting it as *the* physical model, and relating its `Q` to any EBU quantity, both require prospective authorization that does not exist (§16). |

### 1.3 What can be designed now versus what cannot

**Can be designed now, with no new mathematics and no new authority** — note
that these are *definitions, procedures and criteria*, not results: the form of
the state space, the shape of the block transition law, the conservation
argument and the finite check it reduces to, the *definition* of the autonomous
invariant set, a transparent non-EBU comparison policy, the viability-kernel
recursion and its information-pattern choice, the dimensionless screening
groups, and the diagnostic case separation for three of its four cases.
**Nothing here has been instantiated, enumerated, or computed.**

**Cannot be designed now:** any mapping from this world's conserved quantity `Q`
to any EBU quantity; any account, permission, settlement, or affordability
layer; and therefore diagnostic **Case 2** ("a viable action existed but the
permission layer blocked it"), which has no substrate in this repository at all
(§12.4).

**Deliberately not designed here:** growth, topology rewriting, refinement,
joint-action valuation, allocation, and settlement. Each is a later stage with
its own authority.

---

## 2. Scope, and what this memo is not

This memo does **not**:

- adopt, select, preregister, or authorize any world;
- claim that EBU has been validated, that the EBU unit has been established, or
  that any EBU controller is authorized;
- repair, reinterpret, adopt, extend, or execute
  `V3.0_LONG_HORIZON_NORMALIZED_MECHANISM_CANDIDATE.md`, which remains
  **"PROPOSED, NOT ADOPTED"** at line 3 of that file, and whose logistic
  regeneration has **no declared reservoir debit and no conserved total** —
  that document is not conservative and is not called conservative here;
- call the proposed world `SD-01`, contribute to any SD stage, alter any SD
  stage, or claim that any canonical SD prerequisite is satisfied;
- integrate into the books programme or authorize the I-3 boundary/conservation
  profile extension, which `EBU_FUTURE_BOOKS_STRUCTURE.md:1077` explicitly
  gates behind "a later, separate I-3 authorization";
- propose a host, price, budget, or compute plan.

### 2.1 A limit that governs the whole memo

The conservation established here is **mathematical and accounting
conservation of a declared quantity `Q` inside a declared model**. It is *not* a
claim of real-world physical realism, not a claim that `Q` is energy, mass, or
any physical carrier, and not a claim that the model is physically complete.

This limit is not a disclaimer added for caution; it is imposed by this
repository's own conservation authority, which states that a Level 3 isolated
claim "is admissible only if the modeled system is isolated with respect to the
conserved quantity and the state includes all relevant physical forms", and that
"a coordinate described only as useful stock, reserve, service capacity, burden,
or EBU is not automatically a complete physical carrier coordinate"
(`CONSERVATION_AND_BOUNDARY_ACCOUNTING_FOUNDATION.md` §3.3). The world proposed
here declares a single abstract carrier called a **token**. Whether a token
models anything physical is outside this memo and is not claimed.

---

## 3. Literature and theory basis

Annotated prior-art map. Verification status is carried honestly:
`VERIFIED` = confirmed against a publisher/arXiv/abstract record;
`BIB` = taken from a primary paper's own reference list;
`UNVERIFIED` = secondary summary only.

### 3.1 Number-conserving cellular automata

| Source | Supports | Does **not** establish |
|---|---|---|
| Hattori & Takesue (1991), *Additive conserved quantities in discrete-time lattice dynamical systems*, Physica D 49(3):295–322, DOI 10.1016/0167-2789(91)90150-8. `VERIFIED` | Necessary-and-sufficient criterion for additive conserved quantities in 1D discrete-time lattice systems; separates conservation from merely propagative quantities. The historical root of the criterion line. | Stated for nearest-neighbour rules in one dimension. Not a higher-dimensional or arbitrary-radius theorem. |
| Boccara & Fukś (1998), *Cellular automaton rules conserving the number of active sites*, J. Phys. A 31:6007–6018. `BIB` — and Boccara & Fukś (2002), *Number-conserving cellular automaton rules*, Fundamenta Informaticae 52:1–13 (DOI/pages `UNVERIFIED`) | An explicit necessary **and** sufficient condition for a 1D q-state rule to be number-conserving — the checkable per-rule test the fallback family would use. | A criterion, not a construction method. Says nothing about vector-valued or multi-species quantities. |
| Durand, Formenti & Róka (2003), *Number-conserving cellular automata I: decidability*, TCS 299(1–3):523–535, DOI 10.1016/S0304-3975(02)00534-0; preprint arXiv:nlin/0102035. `VERIFIED` | The competing definitions of number-conservation are equivalent, and number-conservation is decidable in **quasi-linear time** from the rule table alone. | Decidability of *conservation* implies nothing about decidability of the *dynamics*. Reachability and long-run behaviour remain hard. |
| Bernardi, Durand, Formenti & Kari (2005), TCS 345 (pages `UNVERIFIED`) | The *number-decreasing* property is decidable in dimension 1 and **undecidable in dimension ≥ 2** — conservation-adjacent properties are dimension-sensitive. | Does **not** say number-conservation itself becomes undecidable in 2D; it remains decidable. |
| Moreira (2003), *Universality and decidability of number-conserving cellular automata*, TCS 292:711–721; arXiv:nlin/0306032. `VERIFIED` | Intrinsically universal NCCA exist: **conservation costs nothing in expressiveness**. A conservative world can still host arbitrarily rich dynamics. | Universality is simulation capability, not tractability, interestingness, or analysability. |
| Fukś (2000), in *Hydrodynamic Limits and Related Topics*, AMS, pp. 57–69 `BIB`; Kari & Taati (2008), *A particle displacement representation for conservation laws in two-dimensional cellular automata*, Proc. JAC 2008, pp. 65–73. `BIB` | **The "local current exists" pair.** For any number-conserving CA the dynamics can be rewritten as explicit particle movements — equivalently a local flow obeying a discrete continuity equation — in **1D** (Fukś) and **2D** (Kari & Taati). | **The representation is not known to exist in dimension ≥ 3; that is an open question.** The 2D result is additionally qualified to context-free conservation laws. Do not state "a local current always exists" unqualified. |
| Pivato (2002), *Conservation laws in cellular automata*, Nonlinearity 15(6), DOI 10.1088/0951-7715/15/6/305; arXiv:math/0111014. `VERIFIED` (pages `UNVERIFIED`) | Conservation over a general discrete abelian group reduces to a **finite system of linear equations** over the neighbourhood, hence is decidable; also gives recipes for *constructing* rules with prescribed conservation laws. | The strongest flux/particle-displacement constructions confirmed are 1D propositions. |
| Redeker (2023/2025), *An Invitation to Number-Conserving Cellular Automata*, arXiv:2308.00060. `VERIFIED` | Current citable survey; states the 1D flow-function form usably. | A survey, not the origin of the theorems. |

### 3.2 Reversible, partitioned, and block cellular automata; lattice gas

| Source | Supports | Does **not** establish |
|---|---|---|
| Margolus (1984), *Physics-like models of computation*, Physica D 10:81–95 (pages `UNVERIFIED`); Toffoli & Margolus (1987), *Cellular Automata Machines*, MIT Press, ISBN 9780262200608. `VERIFIED` | **The block-partitioning scheme**: partition the lattice into disjoint blocks, apply a block-local map, alternate the partition offset each step. Invertibility and conservation become properties of a **finite table you can enumerate**, not global proof obligations. | Block structure buys conservation *within a block*. It certifies nothing about emergent macroscopic behaviour, mixing, or ergodicity. |
| Morita & Imai (2001), *Number-conserving reversible cellular automata and their computation-universality*, RAIRO-ITA 35(3):239–258. `VERIFIED` via Numdam. Also Morita & Harao (1989) `UNVERIFIED`. | **The strongest "conservation by construction" citation.** In partitioned CA, each cell is split into parts and **local reversibility of the part-wise map is equivalent to global reversibility** — a global property reduced to a finite local check. Morita & Imai's number-conserving PCA represent each cell as a triple of non-negative integers whose global sum is conserved throughout evolution, and prove computation-universality. | The precise internal lemma and its number are `UNVERIFIED` (full text not read). Do not cite a theorem number. |
| Hardy, Pomeau & de Pazzis (1973), J. Math. Phys. 14(12):1746–1759, DOI 10.1063/1.1666248 `VERIFIED`; Frisch, Hasslacher & Pomeau (1986), Phys. Rev. Lett. 56(14):1505–1508, DOI 10.1103/PhysRevLett.56.1505. `VERIFIED` | The **collide-and-propagate** template: collisions are permutations of the site occupation vector chosen to fix mass and momentum; propagation is a lattice permutation. Both are bijections, so exact integer conservation holds by construction of the collision table. | HPP's lattice symmetry is too weak for isotropic hydrodynamics — **conservation alone does not buy correct macroscopic behaviour**. Lattice Boltzmann is *not* exactly conserving in the same sense; no claim is made for it here. |

### 3.3 Conservative dynamics on changing topology

| Source | Supports | Does **not** establish |
|---|---|---|
| Arrighi & Dowek, *Causal graph dynamics*, arXiv:1202.1098; ICALP 2012, DOI 10.1007/978-3-642-31585-5_9; Information and Computation, DOI 10.1016/j.ic.2012.10.019 (volume/pages `UNVERIFIED`). arXiv `VERIFIED` | The formal home for worlds whose *topology* changes: bounded-degree time-varying graphs with shift-invariance and causality, and an equivalence between causality and localizability. | **The formalism does not carry conserved quantities.** No source was found formalising additive conservation laws for causal graph dynamics. This is a genuine gap in the literature, reported as such. |
| Arrighi, Martiel & Perdrix, *Reversible Causal Graph Dynamics*, RC 2016, DOI 10.1007/978-3-319-40578-0_5; arXiv:1502.04368; Natural Computing, DOI 10.1007/s11047-019-09768-0. arXiv `VERIFIED` | Reversible causal graph dynamics admit a **block representation** as finite-depth circuits of local reversible gates — the graph analogue of the Margolus block trick. "Vertex-preservation" is the nearest thing here to a conserved quantity. | Scope of the vertex-preservation statement is `UNVERIFIED` (body not read). Vertex count is not a resource invariant. |
| DPO (double-pushout) graph rewriting; chemical graph transformation (Andersen, Flamm, Merkle, Stadler and collaborators). `UNVERIFIED` | In chemical graph transformation the DPO span **defines a bijection of atoms between the two sides of a rule** — conservation by *rule shape*. | **No primary source establishes additive-invariant preservation as a general DPO theorem.** DPO preserves the structural interface, not a numeric additive invariant, unless rules are written to preserve one. |
| Israeli & Goldenfeld (2004, 2006), Phys. Rev. Lett. 92:074105; Phys. Rev. E 73:026203; arXiv:nlin/0508033. `UNVERIFIED` | Local coarse-grained descriptions of CA can be constructed across Wolfram classes. | **Not about conservation.** No source was found proving that conservation laws survive CA coarse-graining or refinement. |

### 3.4 Conservative transport, chip-firing, and the agent-resource precedent

| Source | Supports | Does **not** establish |
|---|---|---|
| Ford & Fulkerson (1956), *Maximal flow through a network*, Canadian J. Math. 8:399–404. `VERIFIED` | Flow conservation at internal nodes, and max-flow/min-cut duality, as the standard statement of a bottleneck. | **A static optimisation constraint, not a dynamical law.** Nothing evolves; there is no time step and no update rule. |
| Dhar (1990), Phys. Rev. Lett. 64(14):1613–1616 (DOI `UNVERIFIED`); Björner, Lovász & Shor (1991), *Chip-firing games on graphs*, European J. Combinatorics 12(4):283–291. `VERIFIED` | Exactly conserving **integer** redistribution on a graph, with the **abelian property**: the stabilised configuration is independent of the order of additions and topplings, hence scheduler-independent and reproducible. | **The abelian sandpile is not globally conserving.** Dissipation at open boundaries or sink sites is *required* for a steady state; grains leave the system. Conservation is bulk-local only. The abelian property concerns the stabilised outcome, not intermediate trajectories, and the model has no agents and no decisions. |
| Bak, Tang & Wiesenfeld (1987), Phys. Rev. Lett. 59(4):381–384, DOI 10.1103/PhysRevLett.59.381. `VERIFIED` | Only the historical point that locally-conserving-with-dissipation toppling can self-organise to a critical state. | **Establishes nothing about conservation as a design guarantee.** Citing it for "conservative dynamics" would be a category error. The 1/f claim is contested downstream. |
| Epstein & Axtell (1996), *Growing Artificial Societies*, Brookings/MIT Press (bibliographic details `UNVERIFIED` from primary) | The canonical shape of an agent-on-a-resource-landscape world: vision, metabolism, accumulated holdings, death at zero. | **Sugarscape is explicitly non-conservative.** Growback creates resource *ex nihilo* at each patch up to capacity, and metabolism destroys it. There is no conserved total. It is prior art for the *shape* of the world and a **counterexample on the conservation axis**. |
| Kehoe (2015), *The Specification of Sugarscape*, arXiv:1505.06012; related MABS 2016 post-proceedings, LNCS 10399, DOI 10.1007/978-3-319-67477-3_3 (attribution `UNVERIFIED`). arXiv `VERIFIED` | The strongest citable evidence for **specification-first world design**: a formal specification "uncovers many ambiguities in the original definition of Sugarscape", gives the first unambiguous interpretation, and identifies where information is missing. | A specification contribution, not a proof of any dynamical property. It does not make Sugarscape conservative and does not verify implementations against the spec. |

### 3.5 Viability and controlled invariance

The load-bearing material for World C is **internal** and is treated in §9.3,
because this repository already contains the exact objects needed and already
records the gap. The external literature supplies the concepts, the correct
terminology, and — importantly — two caveats that change the design.

| Source | Supports | Does **not** establish |
|---|---|---|
| Nagumo (1942), *Über die Lage der Integralkurven gewöhnlicher Differentialgleichungen*, Proc. Physico-Math. Soc. Japan 24:551–559, DOI 10.11429/ppmsj1919.24.0_551. `VERIFIED` (English translation arXiv:2406.18614) | The original tangency criterion: a closed set is weakly forward invariant iff the vector field lies in the contingent cone at every boundary point. The ancestor of "check a local one-step condition everywhere, conclude a global survival property". | Nothing about *controlled* invariance, disturbances, or computation. An ODE existence result, not an algorithm. |
| Aubin (1990), *A Survey of Viability Theory*, SIAM J. Control Optim. 28(4):749–788, DOI 10.1137/0328044. `VERIFIED` | The cleanest citable statement that **viability = controlled invariance under state constraints**. | No discrete or finite-state algorithm. |
| Aubin (1991), *Viability Theory*, Birkhäuser, ISBN 0-8176-3571-8. `SECONDARY` | The canonical definition: `Viab_F(K)` is the set of `x₀ ∈ K` from which **at least one** solution of `ẋ ∈ F(x)` stays in `K` forever, and is the largest closed viability domain in `K`. | **Convexity is load-bearing.** The viability theorem requires `F` to be a Marchaud map — upper semicontinuous, nonempty **compact convex** values, linear growth. Drop convexity and one-step tangency **does not glue into a trajectory**. No theorem numbers cited; the book text was not read. |
| Aubin, Bayen & Saint-Pierre (2011), *Viability Theory: New Directions*, 2nd ed., Springer, DOI 10.1007/978-3-642-16684-6. `VERIFIED` | The modern reference collecting viability kernels, capture basins, and discriminating/leadership kernels in one place. | No finite-state complexity result; its algorithmic chapters target continuous dynamics and grids. |
| Saint-Pierre (1994), *Approximation of the viability kernel*, Appl. Math. Optim. 29(2):187–209, DOI 10.1007/BF01204182. `VERIFIED` | The viability-kernel algorithm: the discrete kernel is an **inner** approximation, and in the Lipschitz case converges using the inflated map `Γ_ρ(x) = x + ρF(x) + (ML/2)ρ²𝔹`. | **The `ρ²` inflation term is essential.** A naive Euler recursion without it is *not* guaranteed to converge. Do not claim the algorithm converges unconditionally. |
| Bertsekas & Rhodes (1971), *On the minimax reachability of target sets and target tubes*, Automatica 7(2):233–247, DOI 10.1016/0005-1098(71)90066-5. `VERIFIED` | The earliest clean **discrete-time** robust backward recursion for keeping a trajectory in a target tube under set-bounded uncertainty — the `∃u ∀d` form, predating viability theory's algorithms. | Not infinite-horizon convergence; not the disturbance-first ordering. |
| Bertsekas (1972), *Infinite-time reachability of state-space regions by using feedback control*, IEEE TAC 17(5):604–613, DOI 10.1109/TAC.1972.1100085. `VERIFIED` | **The caveat that matters most here.** The `n`-step region "may exhibit instability as we pass to the limit", and converges to a steady state only **under a compactness assumption**. The limit of the recursion is *not automatically* the maximal set. | Nothing about finite state spaces — where compactness is free. This is precisely the argument for a **finite** oracle (§9.2). |
| Cardaliaguet (1996), SIAM J. Control Optim. 34(4):1441–1460, DOI 10.1137/S036301299427223X. `SECONDARY` | The **discriminating kernel**: the `∀d ∃u` ordering, in which the controller sees the disturbance's current move. | Not the discrete-time or finite case. |
| Thomas (1995), *On the synthesis of strategies in infinite games*, STACS 95, LNCS 900:1–13, DOI 10.1007/3-540-59042-0_57 `VERIFIED`; Maler, Pnueli & Sifakis (1995), STACS 95, LNCS 900:229–242, DOI 10.1007/3-540-59042-0_76 `SECONDARY`; Grädel, Thomas & Wilke (2002), *Automata, Logics, and Infinite Games*, LNCS 2500, DOI 10.1007/3-540-36387-4. `SECONDARY` | The formal-methods equivalent: synthesis as a two-player game on a graph; the explicit **controllable-predecessor operator**; the attractor construction; and **positional (memoryless) determinacy** of safety games — which is what lets the oracle emit a *stationary* witness policy. | Chapter texts not read; cited for the construction, never for a numbered theorem. |
| Blanchini (1999), *Set invariance in control*, Automatica 35(11):1747–1767, DOI 10.1016/S0005-1098(99)00113-2 `SECONDARY`; Blanchini & Miani (2015), *Set-Theoretic Methods in Control*, 2nd ed., Birkhäuser, DOI 10.1007/978-3-319-17933-9. `VERIFIED` | The terminology this memo uses. **Positively invariant** = no control, trajectories never leave. **Controlled invariant** = *there exists* an admissible control keeping the state inside. **Robustly controlled invariant** = for all admissible disturbances. The distinction is the whole difference between World A and World C and must not be blurred. | Polytope/Lyapunov-centric; no finite-state graph algorithms. |
| De Lara & Doyen (2008), *Sustainable Management of Natural Resources*, Springer, DOI 10.1007/978-3-540-79074-7. `VERIFIED` | The best textbook treatment of **discrete-time** viability for resource systems, including robust and stochastic viability — the closest published analogue to an agent/resource world. | State spaces are continuous or discretised; no finite-state complexity. |
| Béné, Doyen & Gabay (2001), Ecological Economics 36(3):385–396, DOI 10.1016/S0921-8009(00)00261-5 `VERIFIED`; Oubraham & Zaccour (2018), Ecological Economics 145:346–367, DOI 10.1016/j.ecolecon.2017.11.008. `VERIFIED` | Evidence only: viability kernels have been applied to renewable-resource management with joint biological and economic constraints, distinguishing reversible from irreversible crisis. | No method to reuse here; low-dimensional analytic studies. |
| Fijalkow & Horn, *The surprising complexity of generalized reachability games*, arXiv:1010.2420. `VERIFIED` (full text) | Deciding the winner of a reachability game is **linear time, `O(n+m)`** in states and transitions, via the counter-based attractor computation; by duality the same holds for safety. | The linear bound needs the counter-based algorithm; naive greatest-fixpoint iteration is `O(|S|·|E|)`. The Beeri/Immerman attribution and P-completeness are `UNVERIFIED`. |
| Rungger & Tabuada (2017), IEEE TAC 62(7):3665–3670, DOI 10.1109/TAC.2017.2672859; arXiv:1601.00416 `VERIFIED`; Tabuada (2009), *Verification and Control of Hybrid Systems*, Springer, ISBN 978-1-4419-0223-8. `SECONDARY` | That the **maximal** robust controlled invariant set is generally **not finitely computable exactly** for continuous-state linear systems — only δ-complete outer and separate inner approximations. Tabuada supplies the finite-abstraction bridge: abstract, solve a safety game on the finite system, transfer back. | The difficulty is specific to **continuous** state and implies no negative result for the finite case. Abstraction-based synthesis is sound but may be conservative. |

> **Why this matters for the design, and not as decoration.** Bertsekas (1972)
> and Rungger–Tabuada (2017) together say that in the continuous setting the
> exact maximal controlled-invariant set is generally *not* obtainable, and
> Aubin's Marchaud hypothesis says that even existence needs convexity.
> **Finiteness buys all of this for free.** That is the strongest available
> argument for keeping the first world small and exactly enumerable rather than
> starting from a continuous model — and it is an argument from the literature,
> not from implementation convenience.

---

## 4. Candidate world families compared

Seven families were considered against eight requirements. The requirements are
not weighted by implementation convenience.

**R1** exact additive integer conservation · **R2** local flow/current
representation · **R3** finite, exactly enumerable state space · **R4**
heterogeneous per-cell parameters · **R5** persistent actor identity · **R6** a
genuine control input · **R7** conservative topology growth later · **R8**
refinement/coarsening later.

| Family | R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 | Verdict |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|---|
| **Block-partitioned conservative cellular world (integer tokens)** | ✔ by construction | ✔ block-local | ✔ | ✔ | ✔ | ✔ | ◐ | ◐ | **RECOMMENDED** |
| Ordinary number-conserving CA | ✔ by decision procedure | ✔ 1D/2D only | ✔ | ✖ | ✖ | ✖ | ✖ | ✖ | **FALLBACK** (§4.2) |
| Lattice gas (HPP/FHP) | ✔ | ✔ | ✔ | ✖ | ✖ | ✖ | ✖ | ✖ | rejected |
| Abelian sandpile / chip-firing | ◐ bulk only | ✔ | ✔ | ◐ | ✖ | ✖ | ◐ | ✖ | rejected |
| Causal graph dynamics | ✖ no conservation theory | ◐ | ✖ | ✔ | ◐ | ✖ | ✔ | ◐ | rejected for the first world |
| DPO graph rewriting | ◐ by rule shape only | ✖ | ✖ | ✔ | ✔ | ◐ | ✔ | ✔ | rejected for the first world |
| Sugarscape-style agent landscape | ✖ | ✖ | ◐ | ✔ | ✔ | ✔ | ✔ | ✖ | rejected |

### 4.1 Why the recommendation wins

**Conservation becomes a finite check rather than a global proof obligation.**
In a block-partitioned world the update is a map on disjoint blocks, so
conservation reduces to a condition on a *finite table*: every entry must have
equal token sums before and after. Because the blocks partition the world, the
global sum is the sum of block sums, so the table condition gives global
invariance. This is the Margolus/Morita move (§3.2).

> **To be clear about status:** this is a property of the *construction*, not a
> completed verification. No block table has been adopted and no entry has been
> checked. The check itself belongs to rung **L1** of §15.

**Three requirements rule out every classical CA, including the fallback.**

1. **R4 — heterogeneous parameters.** A cellular automaton is by definition a
   *uniform* local rule. But this repository's local potential
   `v_i(x) = α_i[L_i−x]₊² + β_i[x−U_i]₊² + χ_i[R_i−x]₊²`
   (`d0_v29.py:188`) carries **seven per-cell parameters**. Encoding them in the
   cell state to preserve uniformity multiplies the state space and makes
   uniformity vacuous. The recommended world keeps them as declared per-site
   constants and does not pretend to be a uniform CA.
2. **R5 — persistent identity.** CA cells are positions, not entities. An actor
   with a persistent buffer, a persistent demand, and (later) a persistent
   account is not a cell value.
3. **R6 — a control input.** *This is decisive and is easy to miss.* A cellular
   automaton is an **autonomous** system: its next state is `F(x)`. A controller
   experiment requires `F(x, a, d)` — the whole point is that an action is
   chosen. No amount of CA machinery supplies a control input; it has to be
   bolted on, which is precisely the failure the block scheme avoids by making
   the *choice of block map* the control.

**The block partition structurally eliminates joint actions.** Blocks are
disjoint within a tick, so a tick's global action is a product of independent
per-block actions with no cross-block interaction term. With the actor-placement
rule of §5.4, no block ever contains two actors, so **there is no joint action
at all** in the first world — Möbius decomposition, allocation, and settlement
are not deferred, they are structurally absent (§11).

### 4.2 Why the fallback is a real fallback, and what it costs

An ordinary number-conserving CA on the same fixed lattice is the honest
alternative: conservation is then established **after the fact** by the
Boccara–Fukś criterion or the Durand–Formenti–Róka decision procedure (§3.1),
both of which are cheap and total. An author who wants a genuinely uniform-rule
world, with the strongest and oldest body of theory behind it, should take this.

The cost is R4, R5, and R6 — heterogeneous parameters, actor identity, and the
control input all have to be reintroduced by encoding, which is where
specification ambiguity enters. It also inherits the dimensional limit: the
guarantee that a local current representation exists holds in **1D and 2D only,
and is open for dimension ≥ 3** (§3.1). For a small fixed lattice that limit is
not binding, which is why this remains a serious fallback rather than a rejected
option.

### 4.3 Why each rejected family was rejected

- **Lattice gas (HPP/FHP).** The collide-and-propagate discipline is excellent
  and is *borrowed* by the recommendation. But the state is an occupation vector
  over lattice directions, the rule is uniform, and the conserved quantities are
  mass and momentum. Momentum is irrelevant here, and the family supplies
  neither identity nor control. HPP's own history is also the standing warning
  that **conservation does not buy correct macroscopic behaviour** (§3.2).
- **Abelian sandpile / chip-firing.** Very attractive: exactly conserving
  integer redistribution on a graph, with scheduler-independence. Rejected on
  two grounds. First, **it is not globally conserving** — sinks are required for
  a steady state, so grains leave the system, which is exactly the "energy
  vanished" failure the design must exclude. Second, toppling is *forced* when a
  site exceeds threshold; there is no choice, hence no control input.
- **Causal graph dynamics.** The right formalism for changing topology, and the
  reversible variant even has a block representation. Rejected for the **first**
  world because no source formalises additive conservation laws for it (§3.3) —
  adopting it would mean inventing the conservation theory, which is exactly
  what this memo must not do. It is the right candidate for the *later* growth
  extension, once that extension has its own authority.
- **DPO graph rewriting.** Conservation by rule shape (the atom bijection in
  chemical graph transformation) is real but narrow, and **no general
  additive-invariant theorem was found**. It also has no finite enumerable state
  space without extra bounds.
- **Sugarscape.** The shape precedent and the conservation counterexample in one
  object: growback creates resource from nothing. Its second lesson is the more
  useful one — Kehoe's formal specification work shows that an under-specified
  agent world produces implementations that disagree with each other (§3.4).
  That is the reason §5 and §6 below are written as a specification rather than
  as prose.

---

## 5. Formal state definition — the first world `W0`

Everything in this section is **symbolic**. No numerical value is selected.
Where a small illustrative instance is needed, §10.4 supplies one and labels it
non-authoritative.

### 5.1 Geometry — fixed

A ring of `N` sites, `N` even, indexed `i ∈ Z_N`. **The topology is fixed for
the entire first world.** No site is added, removed, refined, or rewired.

Block partition, alternating with tick parity — the 1-D Margolus scheme:

```
P(t) = P_even = { {0,1}, {2,3}, ..., {N-2,N-1} }   if t is even
P(t) = P_odd  = { {1,2}, {3,4}, ..., {N-1,0} }     if t is odd
```

Each `P(t)` is a partition of `Z_N` into `N/2` disjoint adjacent pairs. Every
site belongs to exactly one block per tick.

### 5.2 Reservoirs — explicit, and every one named

Each site `i` carries three integer token counts:

| Coordinate | Meaning | Domain |
|---|---|---|
| `acc_i` | accessible stock — usable this tick | `Z≥0`, capped at `κ_i` |
| `lat_i` | latent stock — present but not usable until mobilised | `Z≥0` |
| `deg_i` | degraded stock — used, not yet recovered | `Z≥0` |

Each actor `a ∈ {1..A}` carries:

| Coordinate | Meaning | Domain |
|---|---|---|
| `buf_a` | internal buffer, the actor's own held tokens | `Z≥0` |

Per-site declared **constants** (not state): capacity `κ_i`, reserve floor
`R_i`, and the potential parameters. `d0_v29.Cell` declares seven per-cell
parameters — `alpha, beta, chi, L, U, R, K` — with `x` as the state value; `W0`
reuses `R` as the reserve floor and `K` as the capacity (written `κ_i` here only
to avoid colliding with the safe set `K` of §7.1). The full seven are
carried but **not used by `W0` itself** — they exist only so that a future EBU
layer would have somewhere to read them from (§12.1).

Per-actor declared constants: home site `h(a)`, buffer floor `β_a`, and the
demand schedule `d_a(t)`.

### 5.3 The conserved quantity

\[
Q=\sum_{i \in Z_N}\left(\mathrm{acc}_i+\mathrm{lat}_i+\mathrm{deg}_i\right)
+\sum_{a=1}^{A}\mathrm{buf}_a .
\]

- **Unit:** `token`. One carrier, one unit, no conversion anywhere.
- **Coefficient vector:** `c_Q = 1` on every coordinate. In the notation of
  `CONSERVATION_AND_BOUNDARY_ACCOUNTING_FOUNDATION.md` §4, the internal
  conservation condition is `c_Q^T S̃ = 0`, i.e. **every transition column sums
  to zero**.
- **Boundary exchange:** `B φ[k] = 0`. There is none. `W0` is closed.
- **Account level:** Level 3 (isolated) *within the declared model only*, with
  the §2.1 limit applying in full.

### 5.4 Actor placement — the rule that removes joint action

> **Placement constraint.** Actor home sites are pairwise at ring distance
> `≥ 2`.

Two sites share a block under `P_even` or `P_odd` if and only if they are
adjacent. Under the placement constraint no two actors are ever adjacent, so
**no block ever contains two actors**, at any tick, under either partition. Each
block therefore hosts at most one decision. This is checkable by inspection of
the placement and requires `A ≤ ⌊N/2⌋`.

### 5.5 Time and the augmented state

Ticks `t = 0, 1, 2, …`. The block partition has period 2. If the demand schedule
`d_a(t)` is periodic with period `p`, define the **phase**

```
φ(t) = t mod L,     L = lcm(2, p)
```

The **augmented state** is `s⁺ = (s, φ)` where `s` is the token configuration.
This matters: the transition law depends on the tick parity and on the demand
phase, so viability must be computed on the augmented space or it is not
well-defined (§9.2).

### 5.6 State-space size

The configuration is `3N + A` non-negative integers summing to `Q`. Without
capacity caps the count is `C(Q + 3N + A − 1, 3N + A − 1)`; capacity caps reduce
it. Static combinatorics, computed for orientation only:

| Shape | `Q` | States (upper bound) |
|---|---:|---:|
| `N = 2` sites (6 coords) + 2 actors → 8 coords | 16 | 245,157 |
| `N = 2` sites + 2 actors → 8 coords | 24 | 2,629,575 |
| 3 stock coords + 2 actors + 2 reservoir coords → 7 coords | 12 | 18,564 |
| 3 stock coords + 2 actors + 2 reservoir coords → 7 coords | 20 | 230,230 |

> **A limit that must not be promised.** The same formula at 16 sites is
> astronomically large: 18 coordinates with `Q = 32` gives more than
> `6 × 10¹²` configurations. **Exact enumeration is feasible for the tiny world
> and is not feasible at 16 sites.** Any growth extension must state how
> viability is to be established there — by symmetry reduction, by symbolic
> (BDD) representation, by finite abstraction in the sense of Tabuada (§3.5), or
> by an explicitly weaker claim — and **this memo does not solve that.**

The binding constraint is the *state and edge count*, not the fixpoint
algorithm: the fixpoint is `O(n+m)` with the counter-based attractor
computation and `O(|S|·|E|)` naively (§3.5), while `|E| = |S| · |A| · |D|` and
`|S|` grows as a product over reservoir dimensions. As a rough engineering
orientation — **an estimate, not a cited result, and not a commitment** —
explicit enumeration is comfortable to order `10⁷` states and strained by `10⁸`.
The tiny worlds tabulated above sit three to four orders of magnitude inside
that; 16 sites sits five orders outside it.

---

## 6. The local conservative transition law

### 6.1 The four transition types form a closed cycle

Every transition moves tokens between named coordinates. There is no creation
and no destruction, and every arrow has a stated origin and destination.

```
        mobilisation              consumption
   lat ─────────────────> acc ─────────────────> deg
    ^                      │                      │
    │                      │ transport            │
    │                      │ (acc_i -> acc_j)     │
    │                      v                      │
    └──────────────────────────────────────────────┘
                     recovery (deg -> lat)
```

| Transition | Effect | Cap | Note |
|---|---|---|---|
| **Mobilisation** `M_i(g)` | `lat_i −= g`, `acc_i += g` | `g ≤ min(lat_i, m_i, κ_i − acc_i)` | The regeneration analogue. **It debits an internal reservoir.** |
| **Transport** `T_{ij}(q)` | `acc_i −= q`, `acc_j += q` | `q ≤ min(acc_i, c, κ_j − acc_j)`, `{i,j} ∈ P(t)` | Lossless, integer, block-local. |
| **Draw** `D_a(q)` | `acc_{h(a)} −= q`, `buf_a += q` | `q ≤ min(acc_{h(a)}, ν_a)` | Actor takes stock into its buffer. |
| **Consumption** `C_a(u)` | `buf_a −= u`, `deg_{h(a)} += u` | `u ≤ buf_a` | **Metabolism is a transfer, not destruction.** |
| **Recovery** `V_i(r)` | `deg_i −= r`, `lat_i += r` | `r ≤ min(deg_i, ψ_i)` | The slow return path. |

> **No regeneration without a debit.** There is no logistic term and no source
> term anywhere in `W0`. Accessible stock can increase only by mobilisation,
> which subtracts exactly the same integer from `lat_i`. This is the
> `Δ(∑x + z + w) = 0` structure that
> `CONSERVATION_AND_BOUNDARY_ACCOUNTING_FOUNDATION.md` §5.2 sets out as the
> "optional isolated regeneration extension", and which §5.2 is explicit is
> "a new optional model, not a reinterpretation of historical D0 or P1C".
> `W0` uses that structure and makes no claim about D0 or P1C.

A mobilisation **rate cap** `m_i` may depend on the local state (for instance,
on `acc_i` or on `lat_i`), which is where interesting dynamics live. What it may
never do is exceed `lat_i`. When `lat_i = 0`, mobilisation is zero. The world is
finite and knows it.

### 6.2 Update order — explicit and synchronous

Per tick `t`, in this exact order:

1. **Freeze** the complete pre-state `s(t)`. Every subsequent computation in
   this tick reads only `s(t)`.
2. **Select** the partition `P(t)` by tick parity.
3. **Evaluate** demand `d_a(t)` for each actor — deterministic.
4. **Generate** the candidate action set per block from the fixed block
   specification (§6.4). No random menu.
5. **Screen** for physical feasibility and for the homeostatic constraints of
   §7.1. *Inadmissible actions are removed here and can never be recovered
   later.*
6. *(World D only — not present in `W0`, `A`, `B`, or `C`)* evaluate the
   controller's value on the surviving actions and apply account permission.
7. **Select** exactly one action per block, including the declared no-op.
8. **Apply** all block maps against the frozen `s(t)`. Blocks are disjoint, so
   the result does not depend on the order in which they are applied.
9. **Record** the receipt: pre-state, partition, per-block candidate set,
   admissible set, selection, post-state, and the conservation residual.

Step 5 strictly precedes step 6. This ordering is not novel: it is the ordering
this repository already enforces, where P1C "remains the physical permission
layer" and the quote module "receives `q_acc` and quotes only `[0, q_acc]`"
(`ebu_quote_v30.py:24–26`), and where falsifier **F5** is "a positive quote
bypasses P1C" (`v30_quote_validation_plan.json`). A large controller value must
never make an inadmissible action selectable.

### 6.3 Conservation theorem

> **Proposition (exact conservation).** Let every entry of the block
> specification satisfy: the sum of all token coordinates owned by the block is
> equal before and after. Then for every legal tick,
> `Q(s(t+1)) = Q(s(t))`, exactly, over the integers.
>
> *Proof.* `P(t)` partitions `Z_N` into disjoint blocks, so each site's three
> coordinates belong to exactly one block. Each actor's `buf_a` is assigned to
> the unique block containing its home site `h(a)`; uniqueness follows from
> `P(t)` being a partition, and needs no further hypothesis. Hence the
> coordinate set `{acc_i, lat_i, deg_i}_{i∈Z_N} ∪ {buf_a}_a` is partitioned by
> the blocks, and
> `Q = Σ_{B ∈ P(t)} Q_B` where `Q_B` is the block's own token sum. Step 8 applies
> to each block a map that preserves `Q_B` by hypothesis, and applies nothing
> else. Therefore `Q(s(t+1)) = Σ_B Q_B(s(t+1)) = Σ_B Q_B(s(t)) = Q(s(t))`. All
> quantities are integers, so equality is exact and no tolerance is involved. ∎

Two things make this short. Blocks are **disjoint**, so there is no
double-counting to rule out. Blocks **cover** the coordinate set, so there is no
residue outside the sum. Each of the five transition types in §6.1 visibly
satisfies the hypothesis: each moves an integer `g, q, u, r` from one named
coordinate to another within the same block.

> **What this proposition does not establish.** It does not establish
> homeostasis, stability, viability, efficiency, or that `Q` models anything
> physical. `CONSERVATION_AND_BOUNDARY_ACCOUNTING_FOUNDATION.md` §11 supplies
> the standing counterexample: "a lossless two-state system can conserve a sum
> while deviations grow in opposite directions. Conservation alone does not
> prove Lyapunov stability."

### 6.4 The local flow law

For each site `i`, the change in accessible stock over one tick decomposes as a
discrete continuity relation:

```
acc_i(t+1) − acc_i(t)  =  [ inflow into acc_i ]  −  [ outflow from acc_i ]
                       =  ( M_i + Σ_j T_{ji} )  −  ( Σ_j T_{ij} + D_{a(i)} )
```

with every term a non-negative integer read from the block map that owns `i`.
Summing over `i` and adding the corresponding relations for `lat`, `deg`, and
`buf`, every internal transfer appears exactly twice with opposite sign and
cancels — which is the hierarchical cancellation rule of
`CONSERVATION_AND_BOUNDARY_ACCOUNTING_FOUNDATION.md` §8 — leaving `ΔQ = 0`.

> **This flow is not an EBU flow.** The quantities `M_i`, `T_{ij}`, `D_a`, `C_a`,
> `V_i` are integer token movements. They are **not** `J_e`, **not** `f_e`,
> **not** `Ψ_e`, and **not** `dy`. No identification between them is proposed
> here, and §12 records exactly why none can be proposed yet. Note also the
> literature limit of §3.1: the guarantee that a conserving rule *admits* a
> local current representation is established in 1D and 2D and is **open in
> dimension ≥ 3**. `W0` is 1-D, so the limit does not bind — but it would bind a
> higher-dimensional successor, and that must not be forgotten.

---

## 7. World A — the autonomous conservative world

### 7.1 The homeostasis and viability sets

```
K₀  =  { s :  ∀i,  R_i ≤ acc_i ≤ κ_i }                          (no actors)

K   =  { s :  ∀i,  R_i ≤ acc_i ≤ κ_i    ∧    ∀a,  buf_a ≥ β_a }  (with actors)
```

`K₀` and `K` are **declared constraint sets**, fixed before any result is seen.
They follow the shape this repository already uses: a reserve floor and a
capacity ceiling, as in the registered viability sets `V_H1 = V_H2 = V_H3 =
{x : 5 ≤ x ≤ 20}` and in P1C's safe set `S = {x : x_i ≥ R_i^eff}`.

### 7.2 What "the world survives without actors" means, precisely

World A sets `A = 0` and permits only mobilisation, transport, and recovery.
The system is then **autonomous** — there is no control input — and
deterministic on a finite state space, so every forward orbit is eventually
periodic.

> **Definition.** `Inv(K₀)` is the maximal forward-invariant subset of `K₀`:
> the set of `s⁺ ∈ K₀ × Z_L` whose entire forward orbit remains in `K₀`.

Because orbits are eventually periodic, membership is decidable by following
each orbit until a state repeats, so `Inv(K₀)` **can be computed exactly once
the autonomous transition table, the parameters and `K₀` are adopted**. It has
not been computed, because none of those has been adopted. **World A would pass
if the declared initial family lies in `Inv(K₀)` and `Inv(K₀)` is non-empty** —
that is the criterion, not a result.

This is deliberately not biological language. It is membership in an invariant
set, in the sense that `Blanchini`'s survey separates from *controlled*
invariance (§3.5) — and the distinction is the entire difference between World A
and World C.

### 7.3 What World A is for

World A exists to establish that the world does not collapse because its own
dynamics were badly chosen. If `Inv(K₀)` is empty, the substrate is wrong and
**no** later result about any controller means anything. This must be settled
before actors are added, and it must be settled without any controller present.

---

## 8. World B — a transparent non-EBU policy

### 8.1 The policy, and its relation to the historical baseline

`π_greedy`: *satisfy current demand whenever locally possible.*

At each tick, in each block that contains an actor `a`:

1. draw `q = min(d_a(t) − buf_a, acc_{h(a)}, ν_a)` if `buf_a < d_a(t)`,
   else `q = 0`;
2. consume `u = min(d_a(t), buf_a)`;
3. mobilise and recover at the maximum permitted rate;
4. transport within the block toward the actor's site if the actor is short.

It is shaped **by analogy** with the historical unconstrained baseline
`H0: u = min(d, max(0, x_pre))` and its reserve-respecting sibling
`H1: u = min(d, max(0, x_pre − 5))`, which appear in the SD-01 configuration of
the canonical matrix.

> **The analogy transfers no authority.** `W0` is a different, unregistered,
> integer, multi-reservoir world. `H0` and `H1` are real-valued single-stock
> rules belonging to a registered study on a separate lineage. Citing them
> explains *where the shape of the comparator comes from*; it does not make the
> `W0` comparator registered, derived, or authorised, and it does not import any
> SD-01 parameter. The comparator for `W0` must be declared on its own at
> adoption.

> **It is not a straw man.** `π_greedy` is exactly what a competent engineer
> writes first, and it is optimal for the current tick. Its weakness is
> structural, not silly: it has no representation of the future.

### 8.2 How it loses viability — four mechanisms, none of them non-conservation

| Mechanism | Why `π_greedy` fails | Conservation |
|---|---|---|
| **Distribution** | Stock sits in `acc_j` while the shortage is at `acc_i`. Greedy never moves stock that is not needed *now*. | `Q` unchanged |
| **Bottleneck** | Under the alternating pair partition a token moves **at most one site per tick**, so stock at distance `D` arrives no sooner than `D` ticks. Greedy does not start moving it `D` ticks early. | `Q` unchanged |
| **Reserve depletion** | Greedy draws `acc_i` below `R_i` to satisfy today's demand, leaving `K` permanently. | `Q` unchanged |
| **Degradation lock-up** | Consumption routes tokens into `deg`. If recovery capacity `ψ` is smaller than the degradation rate, `deg` grows, `lat` shrinks, mobilisation starves, and the world runs out of *accessible* stock while `Q` is untouched. | `Q` unchanged |

The fourth is the important one for this design. **Tokens never vanish; they end
up in the wrong reservoir.** That is precisely the required distinction between
"draining the system" and "energy disappeared".

### 8.3 A derived, not tuned, threshold

The bottleneck mechanism yields a condition with no free parameter. Let
`dist(h(a), i)` be ring distance. In the worst case where an actor's supply must
come from the farthest site, a policy without lookahead needs the actor's buffer
to cover the whole transport delay:

```
β_a  ≳  d_a · max_i dist(h(a), i)
```

If `β_a` is below this, some demand pattern will defeat `π_greedy` **for
structural reasons that can be stated in advance**, without running anything.
That is the kind of condition this design is supposed to produce, and it is
derived from the geometry, not fitted to an outcome.

> **Do not optimise this policy, and do not degrade it.** If `π_greedy` turns
> out never to lose viability in the registered regime, that is the result and
> it must be reported. Changing the world afterwards to manufacture a collapse
> is the specific failure this whole memo exists to prevent.

---

## 9. World C — the independent viability oracle

### 9.1 The question it answers

> *Does at least one admissible action policy preserve the declared homeostasis
> condition over the stated horizon?*

The oracle is **not** a competitor to any controller. It does not rank actions,
does not value them, and has no objective. It answers one yes/no question per
state and reports which actions retain the answer "yes".

### 9.2 The recursion, and why it terminates

On the augmented state space `S⁺ = S × Z_L` (§5.5), with demand revealed before
the action is chosen:

```
V₀      =  K⁺
V_{k+1} =  { s⁺ ∈ V_k  :  ∀ d ∈ D(φ),  ∃ a ∈ A_adm(s⁺, d),  F(s⁺, a, d) ∈ V_k }
```

where `A_adm` is the set of actions surviving the §6.2 step-5 screen.

> **Proposition (termination and characterisation).** `S⁺` is finite and
> `V_{k+1} ⊆ V_k` by construction. A decreasing chain of subsets of a finite set
> stabilises in at most `|K⁺|` steps, at a fixpoint `V_∞`. `V_∞` is the maximal
> controlled-invariant subset of `K⁺`: it is controlled-invariant because it
> satisfies the defining condition at the fixpoint, and maximal because any
> controlled-invariant `W ⊆ K⁺` satisfies `W ⊆ V_k` for every `k` by induction. ∎

This is the greatest fixpoint of the controllable-predecessor operator — the
same object as the winning set of a safety game on a finite graph. On a finite
state space the argument above is complete and needs no external authority; the
external viability literature (§3.5) supplies the concept, not the proof.

**Two things make this proposition work, and neither is free in general.**
*Finiteness* gives termination and maximality. Bertsekas (1972) shows that in
the infinite/continuous case the limit of the same recursion need **not** be the
maximal set without a compactness assumption, and Rungger & Tabuada (2017) show
the exact maximal robust controlled-invariant set is generally not finitely
computable for continuous-state linear systems (§3.5). *Finite branching* gives
the memoryless witness: positional determinacy of safety games means the oracle
can emit a **stationary** policy, not merely assert that some policy exists.
Both are reasons to keep the first world finite, and they are reasons from the
literature rather than from convenience.

**Ordering matters, and getting it wrong makes the oracle unsound.** Two forms
exist and they are not interchangeable:

```
(A) demand revealed BEFORE the action
    V_{k+1} = { s⁺ ∈ V_k : ∀d ∈ D(φ), ∃a, F(s⁺,a,d) ∈ V_k }

(B) action committed BEFORE demand
    V_{k+1} = { s⁺ ∈ V_k : ∃a, ∀d ∈ D(φ), F(s⁺,a,d) ∈ V_k }
```

Form (A) is the *discriminating* kernel (Cardaliaguet 1996); form (B) is the
minimax/target-tube form (Bertsekas & Rhodes 1971). Always **(B) ⊆ (A)**, with
equality under an Isaacs-type saddle condition.

> **The trap.** Using form (A) when the real controller must commit its action
> *before* demand realises produces an **optimistic and unsound** oracle: it
> would certify states as viable that the actual controller cannot hold, and
> would then misattribute the resulting failure to the controller as Case 3 when
> it is really Case 1. The declared form must match the controller's actual
> information pattern, or (B) must be computed and (A) treated only as an upper
> bound.

`W0`'s demand is deterministic, so `D(φ)` is a singleton and (A) and (B)
coincide. The ordering must still be written down at adoption, because it stops
being free the moment demand becomes uncertain.

### 9.3 The oracle is necessary, and this repository already says so

This is not a new requirement invented by this memo. The repository already
contains the objects and already records the gap.

`V2.9_OBJECTIVE_ALIGNMENT_REVIEW.md` §5.1 — the independent review whose
Theorem 4.1 `p1c_v29.py:5–7` cites as normative — defines the safe set `S`, the
one-step kernel

```
K₁ = { x ∈ S : x_i + Δt·u_i(x) ≥ R_i^eff  for every critical i }
```

and then states that full controlled invariance "requires the **largest
controlled-invariant subset** `K∞ ⊆ K₁` (the viability kernel), obtained by
iterating the one-step operator until fixed point", and that computing `K∞` "is
an **Open problem**".

Three consequences follow, and the third is the point of World C.

1. **`K₁` is what P1C enforces.** P1C's State-P classifier is exactly the
   condition `x + dt·u ≥ R_eff` (`p1c_v29.py:196–215`).
2. **`K∞ ⊆ K₁` makes `K₁` an *outer* approximation of the viability kernel.**
   Membership in `K₁` therefore does **not** guarantee viability. *(The review
   describes `K₁` as "the one-step conservative inner estimate"; since
   `K∞ ⊆ K₁`, `K₁` is a superset and the word "inner" is the wrong direction for
   a safety certificate. This is a terminological correction, offered as this
   memo's reading; the review's substantive claims — the inclusion, the fixpoint
   characterisation, and the open-problem status — are all consistent and are
   not disputed.)*
3. **The review proves the oracle cannot be replaced by a local rule.** Its
   Impossibility 6.4 states that no single local action-time rate certifies
   long-run sustainability across all source types, and that while "the one-tick
   reserve budget *is* local and universal; **long-run** sustainability is not
   locally certifiable".

So a controller screened only by a one-step barrier can be admissible at every
tick and still walk irreversibly out of viability. **An independent, non-local
oracle is the only thing that can tell the difference**, and this repository has
already established that it does not have one.

The same pattern appears in the registered SD programme: SD-01's `H3` comparator
admits an action only if the next-step admissible set is non-empty **under both**
registered shock branches — a `∀d, ∃a` condition at depth 2. In the notation
above that is `V₂`. Since `V_∞ ⊆ … ⊆ V₂ ⊆ V₁ ⊆ V₀`, `H3` is a **truncation** of
the recursion, and being `H3`-feasible does not imply being viable. That is an
observation about the shape of the registered comparator, not a criticism of it
and not a proposal to change it.

### 9.4 The four diagnostic cases

For a decision at augmented state `s⁺` with demand `d`:

| Case | Condition | Reading | Testable now? |
|---|---|---|---|
| **1** | `s⁺ ∉ V_∞` | The world was already impossible from here. **Do not attribute the failure to the controller.** | **Yes** |
| **2** | `s⁺ ∈ V_∞`, a physically and homeostatically admissible viability-preserving action exists, but the **account/permission layer forbids every one of them** | The permission architecture turned a survivable state into a non-survivable one. Scientifically important. | **No — see §12.4** |
| **3** | `s⁺ ∈ V_∞`, a viable permitted action exists, controller selects `a'` with `F(s⁺,a',d) ∉ V_∞` | The decision rule failed. | **Yes** (once a controller exists) |
| **4** | `s⁺ ∈ V_∞` and the controller stays in `V_∞` | The controller preserved viability under the registered conditions. | **Yes** (once a controller exists) |

The per-decision record required to separate these is: whether `s⁺ ∈ V_∞`; the
candidate set; which candidates were physically admissible; which of those
retained `V_∞` membership; which were permitted; and which was selected.

> **Case 4 must not be made inevitable.** The regime must be chosen (§10) so
> that both Case 3 and Case 4 are reachable. A regime in which every policy
> survives tests nothing.

---

## 10. Regimes — symbolic and dimensionless

### 10.1 Symbols

`N` sites · `A` actors · `Q` total tokens · `d_a` per-actor demand rate ·
`D = Σ_a d_a` aggregate demand rate · `m` aggregate mobilisation cap ·
`ψ` aggregate recovery cap · `c` per-block transport cap · `R = Σ_i R_i` total
reserve floor · `κ` capacity · `H` horizon · `δ` degradation fraction (tokens
routed `acc → deg` per token served; `δ = 1` in `W0`, where consumption is a
full transfer).

### 10.2 Five dimensionless groups

| Group | Definition | What it governs |
|---|---|---|
| `Π₁` | `δD / ψ` | **Long-run closure.** If `Π₁ > 1`, degraded stock is produced faster than recovery returns it, so `lat` drains and mobilisation eventually starves. **This forces failure only if the declared safe/service condition requires demand to be met indefinitely.** If the adopted `K` permits rationing or unmet demand, `Π₁ > 1` is *not* on its own sufficient for non-viability. |
| `Π₂` | `D / m` | **Mobilisation.** Even with closure, accessible stock must be produced fast enough. |
| `Π₃` | `D / c` | **Bottleneck / distribution.** Transport capacity against demand. |
| `Π₄` | `R / Q` | **Reserve tightness.** The fraction of the conserved total locked below floors. `Π₄ → 1` ⟹ reserve-binding. |
| `Π₅` | `H·D / Q` | **Horizon turnover.** How many times the world's whole stock must cycle. Large `Π₅` ⟹ `Π₁` dominates; small `Π₅` ⟹ buffer stock dominates and a world with `Π₁ > 1` can still be transiently viable. |

Each group is dimensionless: `Π₁` is (tokens/tick)/(tokens/tick), `Π₂` and `Π₃`
likewise, `Π₄` is tokens/tokens, and `Π₅` is (ticks · tokens/tick)/tokens.

> **All five are screening heuristics, not classifiers.** Each is a coarse
> necessary-condition indicator derived from rates and totals. None of them
> accounts for the *distribution* of tokens across sites, for timing, or for the
> shape of the adopted safe set `K` — and every one of those can decide
> viability on its own. **Only the exact viability kernel `V_∞`, computed on the
> adopted finite world, classifies that world.** The groups say where to look.

### 10.3 Regime classification

| Regime | Screening condition | Scientific purpose |
|---|---|---|
| **Trivially sustainable** | `Π₁, Π₂, Π₃, Π₄` all ≪ 1 | Control-free positive control. **Not a valid site for a controller experiment** — every policy survives, so the controller cannot matter. |
| **Bottleneck / distribution** | `Π₁ ≪ 1`, `Π₃ ≳ 1` | Isolates routing and timing from scarcity. Tokens are plentiful and in the wrong place. |
| **Reserve-binding** | `Π₄ ≳ 1` with `Π₁ ≪ 1` | Isolates the reserve floor as the binding constraint. |
| **Shock and recovery** | a deterministic, fully registered step in `d_a(t)` | Tests recovery, not survival. |
| **Near-critical** | `Π₁ ≈ 1` | The decision-sensitive band. Both Case 3 and Case 4 must be reachable here. |
| **Intrinsically impossible** | `Π₁ > 1` and `Π₅ ≫ 1` | Negative control. `V_∞` should be empty or the initial state outside it. **Must be run, so that Case 1 is demonstrably detectable.** |

> **The groups screen; they do not classify.** `Π₁…Π₅` say where to look. The
> actual classification of any parameter tuple is by **exact computation of
> `V_∞`**, and nothing else. Substituting the ratios for the oracle would
> reintroduce exactly the heuristic the oracle exists to remove.

**No stochastic shocks in the first world.** `W0` is deterministic. If a shock
schedule is used it is a registered deterministic sequence, written down before
anything runs — matching SD-01's registered `stochastic_rules: FORBIDDEN` and
`seeds: none`.

### 10.4 Illustrative instance — NON-AUTHORITATIVE

To make the specification concrete enough to attack, and for no other purpose:

```
N = 4,  A = 2,  h(1) = 0,  h(2) = 2      (ring distance 2 — placement holds)
Q = 16 tokens
κ_i = 6,  R_i = 1,  β_a = 2
d_a(t) = 1 for all t                      (p = 1, so L = lcm(2,1) = 2)
```

> **These numbers select nothing.** They are chosen to be small enough to
> enumerate and to satisfy the structural constraints of §5.4 — not to produce
> any behaviour. They are not a preregistration, they are not defaults, and no
> later scientific parameter may be inherited from them. Under §11's discipline,
> the scientific parameters must be derived from `Π₁…Π₅` and frozen **before**
> any controller result is visible.

**Nothing is inherited from prior work.** No value from Gate 1D-C, D5, the N/H/X
candidate, or the SD-01 configuration is used as a default here. In particular
the N/H/X world (`x_s` 1.15/1.06/1.02, `R_eff` 1.0, `F = 5`, `η = 0.9`,
`dt = 0.0177936`) is a *different, non-conservative, real-valued* model and
supplies nothing to `W0`.

---

## 11. Joint actions and the interaction boundary

**The first world has no joint actions.** By §5.4 no block ever contains two
actors, and by §6.2 step 8 blocks are disjoint within a tick. A tick's global
action is therefore a product of independent per-block actions with no
cross-block interaction term. There is no joint effect to measure, no
interaction index to compute, and nothing to allocate.

Consequently, and without exception in this design:

- **no settlement**, **no allocation**, **no wallet**, **no causal attribution**;
- **no Möbius or inverse-Möbius decomposition**;
- **no O3 resolution** — `O3` (aggregate multi-edge quote and allocation)
  **remains open** in this repository (`v30_o14_multi_edge_plan.json:140`:
  `"aggregate multi-edge quote/allocation - REMAINS OPEN; no settling aggregate
  arm is registered"`), and `O8` (overexecution settlement) likewise
  (`ebu_quote_v30.py:28`: `"full settlement semantics are OPEN (O8)"`).

**If a two-action extension is ever proposed**, four things must be kept
separate and none may stand in for another:

| Object | Question | Status here |
|---|---|---|
| Joint feasibility | can both actions execute together? | a physical question; permitted later |
| Joint exact evaluation | what is the value of the jointly executed vector? | the repository's registered aggregate form evaluates **the accepted vector, once** — `Δe_group(q_vec) = V_loc(z) − V_loc(z + dt·Σ_e S_e q_e_acc) − Σ_e C_e(q_e_acc)` (`v30_o14_multi_edge_plan.json`) |
| Diagnostic interaction | how far is the joint value from the naive sum? | recorded as `double_count`, explicitly settlement-free |
| Möbius decomposition | how is the joint value attributed to parts? | **not adopted here, and not adoptable while O3 is open** |

The registered aggregate form is quoted only to show that the repository already
distinguishes these and already refuses the fourth. **No allocation of joint
value is adopted in this memo.**

---

## 12. The EBU mapping boundary

This section is the reason the overall verdict is not a clean GO.

### 12.1 The governing law, and its actual status

The repository's exact finite form is

```
Δe(q) = V_loc(z) − V_loc(z + dt·S_e·q) − C_a(q)
```

with `z = x + dt·u(x)` the frozen no-action successor. Its authority chain was
checked, not recalled:

- `ebu_quote_v30.py:12–16` implements it and binds it to
  `v30_quote_validation_plan.json`;
- that plan's **canonical** SHA-256 is
  `a1916e8ecf366cee93a5284a0d8fcb68a3e1a429f49ce62b9f5914df87f94061`, which
  **matches** the digest the module claims (recomputed for this memo over the
  plan's canonical JSON — sorted keys, compact separators, ASCII,
  `allow_nan=False`);
- the plan records `equation`, `one_edge_form`, and
  `settlement: "exact finite-difference value at the measured point of the
  schedule committed before execution; no post-outcome valuation rule"`.

> **But the law is a candidate, not an acceptance.**
> `V3.0_LOCAL_EBU_FOUNDATION_DRAFT.md:1141` places it under **"Candidate designs
> (not adopted as truth)"**: "6.5 (the exact quote law itself — the object Gate 1
> must validate and attack)". This memo therefore identifies only what would be
> required *before a later controller could use the repository's current
> candidate law*. It does not validate EBU, does not establish the EBU unit, and
> authorizes no controller.

### 12.2 Quantity-by-quantity inventory

| Quantity | Status | Detail |
|---|---|---|
| `V_loc` | **partially derivable; a declaration is missing** | `v_i(x) = α[L−x]₊² + β[x−U]₊² + χ[R−x]₊²` (`d0_v29.py:188–194`). With rational parameters and integer `x` it is an **exact rational** — so it is evaluable on `W0` without floating point. **But** it is defined over the D0 single reduced-stock coordinate. Which of `W0`'s coordinates (`acc`, `lat`, `deg`, `buf`) enter `V_loc`, and with what parameters, is **unregistered**. |
| `μ = ∇V` | derivable | `marginal()` (`d0_v29.py:197–207`), same coordinate question. |
| `f_e = μ_i − η_e·μ_j` | **not applicable as written** | `W0`'s transport is lossless integer (`η = 1`) with degradation as a *separate typed transition*. The two-endpoint lossy form does not describe a three-way `acc_i → acc_j`, `acc → deg` structure. Independently, it is **unregistered for SD-03**, whose configuration "declares **no edge, no threshold `theta_e`, no mobility `M_e` and no efficiency `eta_e`**" (`SD_03_PRE_EXECUTION_READINESS.md` §4). |
| `J_e = M_e[f_e − θ_e]₊` | **missing** | Requires `M_e`, `θ_e`, which nothing declares for such a world; and it would have to be integer-valued in `W0`, which the Onsager form is not. |
| `Ψ_e` | **missing** | Unregistered, and its "derivation is itself registered as pending future Part I work under separate authority" (`SD_03_PRE_EXECUTION_READINESS.md` §4). |
| `γ_e`, `dy` | **not required** | The committed settlement form is the **endpoint difference**, not a quadrature. The draft's Observation 6.12 records that the exact form *equals* the path integral of the loss-aware force — a proved statement about the same object, not a second thing to supply. The module is explicit that the value is "never a quadrature, never a series, never a surrogate". |
| `C_a` | **a declaration is required** | The `ProcessCost` type exists with `C(0) = 0`, `C ≥ 0`. Which process burdens `W0`'s actions carry is undeclared, and any declaration must satisfy the Gate-1A.1 no-double-count restriction: `C_a` prices "**unrepresented action process burden**" only, never a state-carried burden already inside the `V_loc` difference (`ebu_quote_v30.py:56–68`). |
| `potential-unit → EBU-unit` | **missing** | `SD_03_PRE_EXECUTION_READINESS.md` prerequisite **P5**: "The chain ends in an 'EBU-unit' that nothing defines in terms of the potential." *Partial mitigation:* a **ranking** among admissible actions is invariant under any strictly increasing identification. Magnitude comparison, cross-world comparison, and any settlement are **not**. |
| account `B_i(t)`, permission, settlement | **does not exist** | See §12.4. |

### 12.3 A property worth noting, and its limit

Because `Δe` is an exact endpoint difference of `V_loc` minus `C_a`, any action
sequence returning the world to its starting configuration yields a net value of
exactly `−Σ C_a ≤ 0`. The `V_loc` terms telescope. This is structurally
consistent with the registered falsifier **F3**, "a closed undriven damage-repair
cycle earns positive net EBU", and with **F2**, "natural regeneration produces
actor credit".

> **This is an observation about the algebraic form, not a validation.** It says
> the shape of the equation does not obviously admit a particular cycle exploit
> on this world. It does not establish that the law is correct, does not
> discharge F2 or F3, and does not substitute for SD-03.

### 12.4 The blocker that removes a whole diagnostic case

**There is no EBU account, wallet, balance, permission, or settlement layer in
this repository, by design.**

- `p1c_v29.py:19` — P1C "implements NO ecological debt, NO EBU, NO wallet, NO
  scalarisation, NO restoration credit, NO resource-conversion price";
- `V3.0_LOCAL_EBU_FOUNDATION_DRAFT.md:5` — the foundation "implements nothing: no
  EBU engine, no wallet, no market, no exchange, no actor economy";
- `ebu_quote_v30.py` — the settlement record "is an audit record, not a wallet";
- `v30_o14_multi_edge_plan.json:194` — "cumulative signed EBU is an evaluation
  variable, not a wallet";
- `O3` and `O8` are both **open** (§11).

Therefore the hard-permission condition — *an actor lacking sufficient permitted
balance absolutely cannot execute* — **has no substrate**. It cannot be
implemented, and it must not be invented, softened into a penalty, or folded
into a selection weight.

> **Consequence.** Diagnostic **Case 2** — "physically viable, but the account
> or permission layer removed every viable action" — is **not testable** and
> cannot be made testable by anything in this memo. Any future experiment
> claiming to separate all four cases must first register account semantics.
> Until then the honest scope is Cases 1, 3, and 4.

### 12.5 EBU bridge verdict

**BLOCKED.** Minimum set of missing authority, stated narrowly:

1. **Acceptance of the quote law itself** (currently a candidate design).
2. **Which `W0` coordinates enter `V_loc`, with which parameters.**
3. **`f_e`, `Ψ_e`, `J_e` for a lossless-integer, three-way transition** — or an
   explicit narrowing of the chain to the links that can be evaluated. (SD-03's
   own prerequisite **P1** makes the same point for SD-03's domain.)
4. **The `potential-unit` → `EBU-unit` identification** (SD-03 **P5**).
5. **A `C_a` declaration** for `W0`'s action set, satisfying no-double-count.
6. **Account, permission, and settlement semantics** — required only if Case 2
   is in scope; `O3`/`O8` are the standing open problems.

Items 1–5 are needed before any controller step. Item 6 is needed only for
Case 2. **None of them is filled in by this memo.**

---

## 13. Growth, refinement, and what is deliberately out of scope

**The first world has a fixed topology.** Growth, topology rewriting, causal
graph dynamics, and refinement are later extensions with their own authority.
This section records only that the substrate does not *preclude* them.

### 13.1 Growth would preserve `Q` trivially

Activating a site whose coordinates are all zero, or adding one, changes no
token count, so `Q` is unchanged by inspection. More generally, any structural
change whose new columns satisfy the §5.3 zero-column-sum condition preserves
`Q`. Both the **activation** model (a larger domain exists from the start, part
of it latent) and **true dynamic topology** are compatible with the invariant;
activation additionally keeps the global state dimension fixed, which makes
exact enumeration arguments easier.

The distinction that matters is already registered elsewhere in the programme:
capacity, population, and topology may grow **while the conserved quantity does
not**. The registered growth campaign states it directly — expansion of
population, carrying capacity, or topology "does not add physical stock", and
"delivery capacity is not resource stock".

> **But exact viability does not scale.** §5.6 shows exact enumeration is
> infeasible at 16 sites. A growth extension must state how viability is to be
> established there, or weaken its claim. **This memo does not solve that**, and
> a growth study must not blame a controller for a topology path whose viability
> was never established.

### 13.2 Why causal graph dynamics is the right *later* candidate

It is the formalism built for local dynamics on changing topology (§3.3). It is
rejected for the first world for one reason only: **no conservation theory
exists for it**, and adopting it now would mean inventing that theory. If a
future growth stage needs genuine graph rewriting, closing that gap is a
research task in its own right and should be named as one.

### 13.3 Refinement — invariant yes, behaviour no

Splitting a site `i` into `i₁, i₂` with `acc_i = acc_{i₁} + acc_{i₂}` (and
likewise for `lat`, `deg`) preserves `Q` **by construction**: the refinement is
an additive decomposition, so the coefficient vector `c_Q = 1` is unchanged.
Coarsening is the inverse sum and preserves it equally.

> **What does not follow.** Preservation of the *invariant* is not preservation
> of *behaviour*. Whether a refined structure is dynamically equivalent to its
> parent — and whether a previously computed result may therefore be reused — is
> a separate question with its own equivalence conditions, invalidation
> requirements, and negative controls. The literature is also silent here: no
> source was found proving conservation laws survive CA coarse-graining (§3.3).
> This memo deliberately does **not** answer it and proposes no cache or reuse
> machinery.

---

## 14. Parameter discipline

| Class | Quantities | How fixed |
|---|---|---|
| **Fixed by conservation or dimensional analysis** | `c_Q = 1`; zero column sums; `ΔQ = 0`; the five `Π` groups' *forms* | Not free. Follow from §5.3 and §10.2. |
| **Structural, fixed by the design** | fixed topology; block partition period 2; actor placement distance ≥ 2; one action per block | Declared in §5; changing any of them makes it a different world. |
| **Regime-defining — must be preregistered** | the target values of `Π₁…Π₅`, the horizon `H`, the deterministic demand schedule, the declared `K` | Chosen from the §10.3 classification **before** any controller result is visible, then frozen. |
| **Derived once the regime is fixed** | `m, ψ, c, R_i, κ_i, β_a, d_a, Q` | Solved from the chosen `Π` values and the structural constraints, not picked. |
| **Intentionally unresolved** | `C_a` shape; which coordinates enter `V_loc`; the EBU unit; account semantics | §12. **Must not be guessed.** |
| **Must never be chosen after inspecting outcomes** | all of the above | See below. |

Two rules with no exceptions.

> **No inheritance.** No numerical value is inherited as a default from Gate
> 1D-C, D5, N/H/X, the registered SD-01 configuration, or any prior candidate.
> §10.4's instance selects nothing.

> **No post-outcome tuning.** The sequence *run → dislike the result → change
> the world → rerun → report the second version* is prohibited. It is already a
> registered falsifier in this programme — "silent clamp, early truncation, or
> **post-outcome parameter change**" — and `AGENTS.md` states the same rule:
> "Never tune parameters, worlds, tolerances, classifications, or hypotheses
> after inspecting candidate outcomes."

---

## 15. Execution ladder

Every rung requires its own authorization. No rung authorizes the next.

| Rung | What it does | Establishes | Does **not** establish | Required before it |
|---|---|---|---|---|
| **L−1** *(this memo)* | static design and authority reconciliation | a comparison and a recommendation | nothing empirical; no adoption | — |
| **L0** | **adopt** a world family and a conservation profile; declare `Q`, `K`, the block table, the update order | a fixed, criticisable specification | nothing about behaviour | **the authority in §16** |
| **L1** | static verification of the block table — every entry's token sums, by enumeration of the table | conservation holds by construction | nothing about trajectories | L0 |
| **L2** | exact enumeration of `W0`: reachable set, `Inv(K₀)` (World A), `V_∞` (World C) | whether the world is viable at all, and where | nothing about any controller | L1 |
| **L3** | World B — the transparent non-EBU policy against `V_∞` | whether a no-lookahead policy can leave viability, and by which of the four mechanisms | nothing about EBU | L2 |
| **L4** | 1–2 tick controller smoke test | that the pipeline composes and conserves | no scientific outcome — **and note that a 1-tick run is still a model execution** | L3 **and all of §12.5 items 1–5** |
| **L5** | short finite recovery tests | recovery behaviour on a registered deterministic schedule | long-run behaviour | L4 |
| **L6** | longer recovery and stress tests | near-critical discrimination | a registered study result | L5 |
| **L7** | a registered long-horizon study | whatever its own preregistration says | — | a registered study identity, which does not exist |
| **L8** | growth and scaling | — | — | §13's unsolved scaling question |

**L0 through L3 involve no EBU at all.** That is the substantive finding of this
ladder: a large and scientifically valuable part of the programme — including
the entire viability oracle — can be built and verified **without touching the
EBU bridge**, and therefore without waiting on §12.5.

---

## 16. Authority boundary and the smallest next step

### 16.1 Authority boundary

> **Before implementation, execution, book integration, or SD-stage
> registration, an explicit prospective authorization is required to:**
>
> 1. **choose and adopt a world family** — this memo recommends one and does not
>    adopt it;
> 2. **define its conservation profile** — the declared quantity, its unit, the
>    coordinates in `c_Q`, the boundary, the transition map, and the residual
>    policy; and
> 3. **define the relationship, if any, between the world's physical quantity
>    `Q` and the EBU accounting quantity** — including the explicit option of
>    recording that there is **none**.
>
> Nothing in this memo supplies any of the three.

### 16.2 The smallest next authorized task

Not implementation. A **single bounded prospective authorization document** that
does exactly three things and stops:

1. **Selects one world family** — the recommendation of §1.1, the fallback of
   §4.2, or a stated alternative.
2. **Declares the conservation profile.** The field list already exists in this
   repository and should be reused rather than reinvented —
   `CONSERVATION_AND_BOUNDARY_ACCOUNTING_FOUNDATION.md` §14.2 enumerates:
   profile identifier and version; account level; boundary identifier and
   hierarchy; quantity identifier and units; the state coordinates included in
   `c_Q`; the internal transformation map or declared invariant; boundary-flow
   channels and sign convention; observability status; the exact or
   uncertainty-aware residual policy; and explicit non-claims about isolation
   and completeness. For `W0` the residual policy is **exact integer equality,
   no tolerance**.
3. **States the `Q` ↔ EBU relation, or records that there is none.** Given §12
   the expected honest answer today is *none yet*, together with the §12.5 list
   as the standing prerequisite.

It should **not** choose scientific parameter values, should **not** authorize
code, and should **not** register an SD stage.

**This task has not been begun.**

### 16.3 Decision table

| Decision | Why it matters | Who/what authority resolves it | Blocks first smoke test? |
|---|---|---|---|
| Which world family is adopted | Everything downstream is a property of the choice | Author, via the §16.2 authorization | **Yes** |
| The conservation profile for `Q` | Without it "conservation" is an undefined claim | Author; field list from `CONSERVATION_AND_BOUNDARY_ACCOUNTING_FOUNDATION.md` §14.2 | **Yes** |
| Which coordinates enter `V_loc` | `V_loc` is defined on one reduced stock coordinate; `W0` has four kinds | Author + EBU foundation authority | **Yes** |
| `potential-unit` → `EBU-unit` | The chain ends in a unit nothing defines | SD-03 prerequisite **P5** | **Yes** for any magnitude or settlement claim; **no** for ranking alone |
| `f_e`, `Ψ_e`, `J_e` for a lossless-integer three-way transition | The registered chain cannot be evaluated as written | SD-03 prerequisite **P1**, or a narrowing amendment | **Yes** |
| `C_a` declaration for `W0`'s actions | Must price only unrepresented process burden | Author, under the Gate-1A.1 no-double-count restriction | **Yes** |
| Account / permission / settlement semantics | No wallet or balance exists anywhere | Open problems `O3`, `O8` | **No** for Cases 1/3/4; **Yes** for **Case 2** |
| Acceptance of the quote law | It is recorded as a candidate design | Gate 1 validation, per the foundation draft | **Yes** |
| Registered study identity | This world is not `SD-01` and is not any registered stage | A separate registration or amendment; **not** this memo | **Yes** for any scientific claim; **no** for L1–L3 verification |
| Regime targets `Π₁…Π₅` | Must be frozen before outcomes are visible | Author preregistration | **Yes** |
| How viability scales past the tiny world | Exact enumeration fails at 16 sites | Unsolved; a research task | **No** for `W0`; **Yes** for growth |

---

## 17. Explicit non-claims

This memo does **not** demonstrate, and nothing in it should be read as
demonstrating, that:

- EBU improves survival, is optimal, or is equivalent to viability control;
- the EBU quote law is validated, accepted, or unit-defined;
- any cellular-automaton current equals any EBU flow;
- interaction allocation, Möbius settlement, `O3`, or `O8` is solved;
- a conservative world, a viability oracle, `SD-01`, or an EBU controller has
  been implemented or validated — **none has been, and none was run**;
- the proposed world is physically realistic, or that `Q` is energy, mass, or
  any physical carrier;
- human preferences, economies, or institutions have been modelled;
- economic growth can continue indefinitely in a finite closed-token world;
- all SD studies share one physical model;
- this design is registered, adopted, preregistered, or authorized;
- this design is `SD-01`, contributes to any SD stage, or satisfies any
  canonical SD prerequisite;
- the canonical SD matrix is an operative local authority in this checkout —
  it is on a separate lineage, and it was read here **read-only from the git
  object store** solely to avoid inventing what the programme already registers.

---

## 18. Summary

A deliberately small, fixed-topology, block-partitioned conservative cellular
world with integer token accounting, explicit internal reservoirs, and
persistent actor identities is the best available first substrate. Conservation
is made *finitely verifiable* — a check on a block table, to be performed at L1
after adoption — rather than left as a proof obligation about a global rule; the
world admits heterogeneous parameters, persistent actors, and a real control
input, which no classical cellular automaton does; and the block partition
structurally removes joint action from the first world.
Autonomous viability and actor-loaded viability both *become* exactly computable
at the tiny scale once a transition table, parameters, a safe set and an
information pattern are adopted — **neither has been computed here** — and the
viability oracle is necessary for a reason this repository has already
established rather than one invented here.

The world can be specified with no new mathematics. It cannot yet be connected
to EBU: six named items are missing or unregistered, the quote law is a
candidate rather than an acceptance, and the absence of any account layer
removes one of the four diagnostic cases entirely.

**GO** to specify. **NO-GO FOR ADOPTION**, pending the authorization of §16.2.
