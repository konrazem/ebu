# Restoring tendency — book revision plan

**Plan only. No manuscript is regenerated or edited by this document.**

The intent is that the books become a **reference laboratory of many worked
cases** rather than a narrative with a few illustrations. The case library
(`EBU_RESTORING_TENDENCY_CASE_LIBRARY.md`) supplies the backbone: each `RT-Cnn`
case eventually becomes a worked example with its disturbance, its exact
arithmetic, and its recorded result.

**The governing rule for every example below: a worked example may be written
only from a recorded result, never from an anticipated one.** Where no result
exists, the example is written as an open question with its falsification
criterion, and labelled as such.

---

## 1. Conceptual sequence to be added or rewritten

### 1.1 Equilibrium versus homeostasis

The distinction the programme took three studies to state properly. Equilibrium
is a point; homeostasis is a *tendency*. A system can be homeostatic while
almost never sitting at equilibrium, and can sit near equilibrium without being
homeostatic — an actor pinned there by a quantum ratio is not regulating.

**Source material.** `EBU_RESTORING_TENDENCY_FOUNDATION.md` §1;
`ENDPOINT_SATURATION_FINDING.md` Theorem A as the cautionary case.

### 1.2 The Gaussian potential as a ruler

`V` measures standardized deviation. It is not a cost, not a utility, not a
viability boundary. Its units are synthetic.

**Source material.** Foundation §2.

### 1.3 Why a fixed 95% region is not a viability boundary

The lattice result is the memorable one and belongs early: a region carrying
95% of the reference measure carries **1.4% of the reachable states** in this
world — `H95` is exactly "the reference, or one unit transfer away". A reader
who has not seen this will misread every occupancy number ever reported.

A real critical boundary must come from physics — stock exhaustion,
survivability, hardware failure — and none is declared for the synthetic world.

**Source material.** `GAUSSIAN_HOMEOSTASIS_REFERENCE_REGION.md` §7;
Foundation §2 and §11.

### 1.4 External disturbance versus actor response

The canonical decomposition `x_t -> z_t -> x_{t+1}`, with `dV_actor = -E`
exactly. This is the single most useful analytical device the programme has
produced and should appear before any dynamics discussion. It lets a reader ask
"was that the world or the actor?" of any tick.

**Source material.** Foundation §3, with the exact conformance identities.

### 1.5 Mandatory action, and mandatory negative-EBU action

Why an actor may not preserve a system by refusing to act, and why an actor
facing only damaging options still acts and takes the least damaging one. The
emergency principle belongs here: an emergency that produces `E < 0` and large
deviation is correct behaviour, not failure — the homeostatic question is what
happens afterwards.

**Source material.** Foundation §12. **Caution to carry:** the net-zero group
finding shows a physically inert action can satisfy mandatory action in form
while defeating it in substance; the books must not present mandatory action as
airtight.

### 1.6 Random, aligned and hostile actors

Three postures toward the same signal. The pedagogical point is that the
*interesting* one is random: aligned is a theorem where reversal is available,
and hostile is an adversary. Robustness to indifferent actors is the claim
worth making and the hardest to establish.

**Source material.** `homeostasis/policies.py`; registered report §6.

### 1.7 Restoring drift

`D_A` and `D_T`, with the worked warning that conditioning on `V` alone
misleads — the hostile arm's `V`-projection looks restoring at moderate
deviation purely because arriving there means having earned capacity. This is
the best available teaching example of why the state is `(x, B)`.

**Source material.** Foundation §4–§6; exploratory report §2.

### 1.8 Capacity effects and the gate

The most consequential result the programme has: the restoring tendency under
V1 is produced entirely by the affordability gate, decays monotonically with
accumulated capacity, and vanishes **exactly** at `B_i = 29`, above which
EBU-random is not similar to the control but *identical* to it.

This section should be built around the exact sweep table, because it is short,
exact, and settles the question without statistics.

**Source material.** `capacity_drift_sweep.py`; Theorems R1–R3.

### 1.9 Large shocks, catastrophe and recovery

`RT-C02`, `RT-C05`, `RT-C06`, `RT-C07`. **No results exist**, so these are
written as open questions with their falsification criteria until runs are
recorded.

### 1.10 Bounded fluctuation and what "divergence" may not mean

On a compact simplex the physical state cannot diverge. The correct vocabulary
is outward drift, high-deviation capture, loss of restoring tendency and
excursion non-return. Only the capacity ledger genuinely diverges.

**Source material.** Foundation §9.

### 1.11 Physical critical thresholds

What would have to be declared for a real viability boundary to exist, and why
the synthetic world deliberately has none.

### 1.12 Exact finite examples

The 496-state world is small enough to enumerate completely, which makes it an
unusually good teaching object: every claim in the capacity sections can be
checked by hand or by a short script. A worked appendix enumerating one state's
menu, its 21 EBU values, its owner deltas and its affordability thresholds
would let a reader reproduce the central results independently.

## 2. Corrections that must be carried into any revision

1. **Aligned occupancy is a theorem, not a demonstration.** No text may present
   `O95 = 1` as empirical evidence that EBU produces homeostasis.
2. **Hostile safety is adverse.** The registered result is that affordability
   restricted a hostile actor's menu without restricting its damage, and the
   exact analysis shows it funds one. This must not be softened.
3. **V1's restoring tendency is regime-dependent.** Any statement that EBU
   improves regulation must carry the capacity regime it holds in.
4. **`O95`/`O99` are diagnostics, not definitions.** Retained, downgraded.
5. **A direct capacity transfer between owners exists** as emergent behaviour,
   though not as a primitive operation. Text claiming otherwise must say which
   it means.

## 3. Sequencing

1. Sections 1.1–1.5 can be drafted now; they rest on definitions and theorems.
2. Sections 1.6–1.8 can be drafted now; they rest on registered results and
   exact enumeration.
3. Sections 1.9 must wait for case-library runs.
4. Section 1.12 can be drafted now.
5. Section 2 corrections apply to existing text wherever it already makes the
   relevant claims, and should be applied in the same pass.

## 4. What must not be written

- Any claim generalizing beyond one three-cell complete-topology world with
  `sigma = (1,1,1)` and a single quantum.
- Any Foster–Lyapunov or stability theorem; none is available, for three
  independent reasons recorded in Foundation §10.
- Any behavioural claim about Capacity V2. It has theorems, static conformance
  and an exact envelope, and no behavioural evidence whatsoever.
- Any worked example whose outcome was not measured.
