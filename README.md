# The Energy Balance Project (EBU)

A small, self-contained research model of **homeostasis on a graph**: can purely
*local* rules keep a resource field alive indefinitely, with no central optimizer?
Like Conway's Game of Life, the engine enforces only physics — survival,
oscillation, and collapse must *emerge*, they are never forced.

The repo is a research artifact: a pure-Python simulation engine, a suite of
experiments, and the LaTeX-free machinery that turns those experiments into the
`Energy_Balance_Project_Foundation_*.pdf` papers.

## The idea

A dynamic scalar field `x_i(t) ≥ 0` lives on an `n × n` lattice. Each cell has a
demand, a capacity, a viable band `[L_i, U_i]`, inflow, regeneration, and leakage.
Two things then compete every tick:

- **Natural dynamics** — the no-action counterfactual: inflow, regeneration,
  demand, and leakage update each cell independently.
- **Local actors** — stationary agents that may redirect capacity along lattice
  edges to relieve stress, subject to transport loss and conservation.

Health is measured by a single **homeostatic burden** functional
`B(x) = Σ_i ( α_i[L_i − x_i]₊² + β_i[x_i − U_i]₊² )` — the squared penalty for
being below the viable floor or above the oversupply ceiling. An actor's value is
its **counterfactual impact**, `Impact = B_no-action − B_with-action`: strictly the
harm it prevented.

Everything obeys a set of hard laws (locality, non-negative transport dissipation,
strict conservation via an audited ledger). Homeostasis is never imposed.

## Version history

The model was hardened across five generations, each building on the last
(V2.1 is a paper-only milestone — first long-horizon evidence, no engine change):

| Version | File | What it adds |
|---------|------|--------------|
| **V2.0** | [energy_balance.py](energy_balance.py) | Foundation: field, burden `B`, marginal potential `μ`, gradient-flow actor law, conflict resolution, counterfactual impact. |
| **V2.2** | [ebu_v22.py](ebu_v22.py) | A conservation **ledger** asserted every tick, plus a **safe** discrete movement law: a transfer executes only if it provably lowers `B` this tick (line-searched size, no overshoot). |
| **V2.3** | [ebu_v23.py](ebu_v23.py) | **Regeneration**: external-flow, logistic, Allee, and finite sources; an `H`-horizon actor that declines an action helping now but harming a regenerative source later. |
| **V2.4** | [ebu_v24.py](ebu_v24.py) | Six **protective harvest rules** on a closed Allee economy, separating genuine ecological foresight from an artifact of the accept/reject architecture. |
| **V2.5** | [ebu_v25.py](ebu_v25.py) | An **EBU accounting/incentive layer** over the frozen V2.4 physics: naive vs guarded ledgers. Guarded credit is live-state, telescoping, and debits transport loss and irreversible extraction — it closes enumerated gaming attacks (round-trips, splitting, claiming regeneration, reserve sacrifice) and keeps adversaries at 100% viability, while a naive ledger lets an adversary earn ~730k credit while collapsing every source. |
| **V2.6** | [ebu_v26.py](ebu_v26.py) | **Automated adversarial testing** of the guarded ledger (a falsification study, *not* an economy). A deterministic beam / red-team search hunts for sequences that earn positive net guarded EBU *and* cause persistent physical harm. It rediscovers a naive exploit (positive control). A corrected, properly paired randomized study then found **1 of 12 layouts to be a confirmed profitable persistent-harm guarded exploit** (seed 0: +260 EBU while all sources die, viability→0%). **Guarded EBU is exploitable on at least one topology**; the ledger is reported unchanged (not patched) and the trajectory kept as a regression fixture. |
| **V2.7** | [Foundation_v2.7_math.md](Foundation_v2.7_math.md) | **Mathematical foundation note (no engine change).** Derives the local actor law from a state functional `V_state = B_homeostasis + B_regeneration` and a dissipation potential `Ψ(J)`, separating three laws: the continuous Onsager flux (A), its forward-Euler discretisation (`B_raw`), and the engine's gated line search (`B_safe`). Proves the continuous-time energy–dissipation identity (Theorem 7.1) and corrects the logistic-sustainability, Allee-reserve, loss-aware descent bound, and finite-causal-speed claims. Validated by [test_math.py](test_math.py) (8 groups, 34 regression checks). |
| **V2.8** | [Foundation_v2.8_discrete_draft.md](Foundation_v2.8_discrete_draft.md) | **Discrete mathematical foundation (no engine change, not yet peer reviewed).** A synchronous **discrete** energy–dissipation inequality for **Model D0** — the frozen-state, unconstrained, loss-aware explicit-Euler discretisation of the V2.7 flow — with an explicit finite-step remainder (Theorem 4.4), a **corrected curvature constant** `L_V` that sums simultaneously active penalty weights, one-edge/spectral/active-set/state-specific step-size bounds, a flux-nullspace lemma (`SJ = 0 ⇒ J = 0`), stock/loss ledger, one-tick locality, and Counterexamples A–E. **Model D0 is not the production DE engine family**, and no D0 theorem transfers to it. Validated (not proved) by [test_v28.py](test_v28.py) (11 groups, 132 checks, stdlib-only, hardened spectral solver). Typeset as [Foundation_v2.8_discrete.pdf](Foundation_v2.8_discrete.pdf). |

## What each version means

A one-paragraph plain-language summary per generation. In short:
**V2.0–V2.4 built the experimental world; V2.5 added the first working EBU
accounting mechanism inside that world.** V2.5 is more than the world, but it is
not yet an EBU *economy* — actors earn balances; they do not yet spend them.

- **V2.0 — the physics.** One scalar field on a lattice with hard laws (locality,
  continuity, bounded state, non-negative dissipation, *no enforced homeostasis*).
  Actors respond to a local burden gradient. Survival is never guaranteed by the
  engine; it must emerge — or not.
- **V2.1 — first evidence** *(paper only, engine unchanged)*. With a
  self-regulating sink (proportional leakage), purely local rules hold ~95% of
  cells viable out to 50,000 ticks, but only inside a bounded supply window;
  outside it the field collapses. Aggregate burden can mask a slow death — so
  per-cell viability and long horizons became mandatory diagnostics.
- **V2.2 — trust the accounting.** Every tick reconciles
  `dX = S + G − D − Λ − loss − spill` (asserted, not assumed), and a transfer
  executes only if it provably lowers burden (line-searched size). Result: the
  safe rule can never make the field worse within a tick.
- **V2.3 — regeneration and a surprise.** Sources can regrow (logistic), fail
  below a critical threshold (Allee), or be finite. The naive H-horizon actor —
  expected to protect regeneration — instead destroyed it after a shock (32/32
  sources dead at H=10), because its isolated-action counterfactual over-credits
  harvest as H grows.
- **V2.4 — the control that resolved it.** Optimizing the harvest *quantity* over
  the horizon (`q_H*`) is sustainable, so the V2.3 collapse was an artifact of
  gating an immediately-optimized quantity, not of foresight itself. The cheap
  **threshold-aware burden** (a penalty for dipping toward the Allee reserve)
  matches the ~91–100× more expensive horizon search: preserves every source *and*
  serves 100% of demand. This became the frozen physical baseline (`v2.4.0`).
- **V2.5 — the EBU wind tunnel.** On top of the untouched baseline, actors earn
  EBU for verified, live-state burden reduction and are debited for harm,
  transport loss, and irreversible extraction. A **naive** ledger is demonstrably
  exploitable (an adversary earns ~730,000 EBU while killing every source); the
  **guarded** ledger closes or bounds every hand-written attack, and maximizing it
  coincides with real homeostatic work. The physics trajectory is exactly
  identical when the ledger only observes.
- **V2.6 — hardening the wind tunnel (and a confirmed guarded failure).** A
  deterministic beam / red-team search hunts for sequences that earn positive net
  guarded EBU *and* cause persistent physical harm. It rediscovers a naive exploit
  (positive control passed). The hand-built fixture showed no guarded failure, but a
  corrected, properly paired randomized study found **1 of 12 layouts to be a
  confirmed profitable persistent-harm guarded exploit** (seed 0: a greedy adversary
  earns +260 EBU while every regenerative source dies and viability reaches 0%). So
  **guarded EBU is exploitable on at least one topology** — a falsification result,
  not a security proof. The ledger is left unchanged and the failing trajectory kept
  as a regression fixture; a corrected guarded variant is the next stage. Still no
  economy: actors earn balances, they do not spend them.
- **V2.7 — the mathematical foundation** *(a written note, engine unchanged)*. Instead
  of a new simulation rule, this stage writes the model down: the actor law is derived
  as gradient flow of a *state functional* `V_state = B_homeostasis + B_regeneration`
  under a *dissipation potential* `Ψ(J)`, cleanly separated from three distinct laws —
  the continuous Onsager flux **A**, its forward-Euler discretisation **B_raw**, and
  the engine's exact line search **B_safe** (which is *not* the Onsager flux, even
  losslessly). It proves a continuous-time energy–dissipation identity
  (`dV/dt = Σ μᵢuᵢ − Σ dissipation`, Theorem 7.1) and, in doing so, **corrects** four
  earlier informal claims: logistic `h ≤ ρK/4` gives equilibrium *existence*, not
  sustainability (needs a basin and discrete-stability condition too); the Allee
  reserve `x=A` shifts under drive; the descent step-size bound carries an `η²`
  transport-loss factor; and strict one-hop causality holds only under frozen-state
  simultaneous updates, which the sequential engine does not use. Nothing is proved by
  the tests — [test_math.py](test_math.py) (8 groups, 34 checks) only guards the
  analysis against drift. Two conjectures remain open (a discrete driven bound; the
  reserve-surrogate condition).
- **V2.8 — the discrete foundation** *(a written note + numerical validation, engine
  unchanged, not yet peer reviewed)*. V2.7's energy–dissipation theorem lived in
  continuous time; the engine ticks. V2.8 crosses the first half of that gap: for the
  idealised **synchronous law D0** (all transfers computed from one frozen state and
  applied simultaneously, no clipping, loss-aware force `μᵢ − ημⱼ`), each tick provably
  obeys *drive − dissipation + an explicit step-size penalty* — overshoot a spectral
  step bound and the "stress score" `V` can rise, exactly like too large a learning
  rate. Along the way it **corrects the curvature constant** (`L_V` must *sum*
  simultaneously active homeostatic and reserve weights — the old max-form permits a
  provably bad step, Counterexample E), proves that Onsager flux can never circulate
  invisibly (`SJ = 0 ⇒ J = 0`), and shows with counterexamples why the naive
  loss-blind force can make things worse over lossy edges. **Crucially, D0 is not the
  shipped engine family (DE)**: the DE members split drive from transport, apply
  transfers sequentially against live state, use the loss-blind force where they
  compute one at all, and clip to `[0, K]` — every one of those mechanisms is
  explicitly excluded and listed as an open problem. [test_v28.py](test_v28.py)
  (11 groups, 132 checks, four negative controls, a hardened Jacobi spectral solver)
  validates the note numerically; **passing checks validate implementation examples,
  they do not prove the theorems**.

### Where this sits on the road to an EBU economy

| Layer | Status |
|-------|--------|
| Physical simulated world (field, sources, transport, storage) | Implemented (V2.0–V2.2) |
| Homeostatic movement rules | Implemented (V2.2–V2.4) |
| Regenerative / Allee / finite sources | Implemented (V2.3) |
| Conservation and loss accounting | Implemented (V2.2) |
| Basic EBU rewards and penalties | Implemented (V2.5) |
| Adversarial reward-gaming tests | Hand-written (V2.5) + automated beam/red-team search (V2.6) |
| Automated/learning adversaries, collusion, laundering | Partially (V2.6 beam + coalition search); learning adversary not yet |
| Exchange between actors (paying, transferring EBU) | Not implemented |
| Prices, saving, borrowing, investment | Not implemented |
| Ownership, production, goods | Not implemented |
| Complete monetary replacement | Far in the future |

```
physical world → homeostatic control → [ EBU accounting — we are here ] → EBU exchange → experimental economy
```

We have built the laboratory and the first measuring instrument — not yet the
monetary system. Before any exchange layer, the wind tunnel should be hardened
with automated adversaries, collusion, multi-step attacks, and long-term
manipulation; only if guarded EBU survives that does transferable EBU make sense.

## Key finding (V2.4)

On a closed economy with Allee-threshold sources, the naïve horizon *gate* looks
fine at first but collapses every source: viability falls to **0% by the end**
(42.8% *averaged over the post-shock half*, which is why the mean hides the
collapse), with `32/32 dead` and **no sustained recovery**. The controls that
either **optimize the harvest quantity** (`horizon_opt`) or **penalize dipping
into a regenerative reserve** (`threshold_penalty`, `hard_reserve`) keep every
source alive *and* serve all demand. Runtime, 1000 ticks; shock at tick 500;
"sust.rec" = ticks to regain ≥90% viability *and* stay there ≥100 ticks:

```
rule               viable%(end) viable%(2ndH) served%   dead   stock  sust.rec
safe                     100.0        100.0     100.0   0/32   587.2       1
horizon_gate               0.0         42.8      73.8  32/32     0.0    none
horizon_opt              100.0        100.0     100.0   0/32   584.7       5
threshold_penalty        100.0        100.0     100.0   0/32   586.6       1
hard_reserve             100.0        100.0     100.0   0/32   587.2       1
penalty_horizon          100.0        100.0     100.0   0/32   584.8       3
```

The key control is `horizon_opt`: choosing the harvest quantity to *maximize* the
H-tick impact is sustainable, so the `horizon_gate` collapse was an artifact of
gating an immediately-optimized quantity — **not** evidence that foresight itself
is harmful.

Across 20 randomized clustered layouts, foresight-based rules beat the safe
baseline on **viable-cell fraction** in all **20/20** paired layouts — a paired
mean of **+22.3 percentage points of viability** (this figure is viability, not
burden).

## Repository layout

```
energy_balance.py       V2.0 engine (Grid, Actor, burden, one synchronous tick)
ebu_v22.py              V2.2 safe engine + conservation ledger
ebu_v23.py              V2.3 regeneration + horizon-aware actor
ebu_v24.py              V2.4 six harvest rules
ebu_v25.py              V2.5 EBU accounting layer (naive vs guarded)
ebu_v26.py              V2.6 automated adversarial search (beam / red-team)
ecosystem.py            self-sustaining producer/consumer ecosystem experiment
exp_v2*.py              experiment drivers (print tables, write figures)
audit_v231.py           conservation-ledger audit
test_*.py               tests per version
make_paper*.py          render the PDF papers via reportlab
figures/                generated plots (burden vs time, phase maps, heatmaps, …)
results/v2.4/           frozen result captures + manifest for the v2.4.0 release
results/v2.6/           adversarial-search results + manifest (V2.6 branch study)
results/v2.7/           manifest for the V2.7 math foundation stage
results/v2.8/           V2.8 validation capture + reproducibility manifest
*.pdf                   the Foundation papers, V2.1 → V2.8
ecosystem.gif           animation of the ecosystem run
```

## Getting started

Requires Python 3.10+ (uses `list[float]` syntax and `from __future__ import annotations`).

```bash
python3 -m venv venv
source venv/bin/activate
pip install numpy matplotlib pillow reportlab
```

Run the foundational demo (a small grid, one actor relieving a deficit):

```bash
python energy_balance.py
```

Run the long-horizon ecosystem experiment (local rule ON vs OFF):

```bash
python ecosystem.py
```

Reproduce the V2.4 results and figures:

```bash
python exp_v24.py            # six rules on the closed Allee economy
python exp_v24_clustered.py  # randomized clustered layouts
```

Regenerate a paper PDF:

```bash
python make_paper_v24.py     # -> Energy_Balance_Project_Foundation_v2.4.pdf
```

Run the tests (plain standard-library scripts — no `pytest` required):

```bash
python3 test_energy_balance.py   # V2.0 core        (8 tests, stdlib only)
python3 test_v22.py              # V2.2 ledger+safe  (7 tests, stdlib only)
python3 test_v23.py              # V2.3 regeneration (4 tests, needs requirements.txt)
python3 test_v24.py              # V2.4 harvest rules(5 tests, needs requirements.txt)
python3 test_v25.py              # V2.5 EBU ledger   (9 tests, needs requirements.txt)
python3 test_v26.py              # V2.6 adversary    (15 tests + reruns the 33 prior)
python3 test_math.py             # V2.7 math regression (8 groups, 34 checks, stdlib only)
python3 test_v28.py              # V2.8 numerical validation (11 groups, 132 checks, stdlib only)
```

Three separate suites (kept separate on purpose — never combine these counts, and a
check count is not a theorem count):

```
Prior engine/ledger: 48 tests
V2.7 mathematical regression: 34 checks in 8 groups
V2.8 numerical validation: 132 checks in 11 groups
```

- **Prior engine/ledger tests — 48 total** (33 prior + 15 V2.6; `test_v26.py` reruns
  the 33 prior as its first test).
- **V2.7 mathematical regression — 34 numerical checks in 8 groups**
  (`test_math.py`). These *validate* the derivations in
  [Foundation_v2.7_math.md](Foundation_v2.7_math.md) at tested points; a passing run is
  not a proof, and the check count is not a count of theorems.
- **V2.8 numerical validation — 132 checks in 11 groups** (`test_v28.py`, deterministic
  seed 20260726, four negative controls, hardened Jacobi spectral solver with
  convergence/residual/PSD guards). These validate the **Model D0** results of
  [Foundation_v2.8_discrete_draft.md](Foundation_v2.8_discrete_draft.md) (typeset as
  [Foundation_v2.8_discrete.pdf](Foundation_v2.8_discrete.pdf)) on declared fixtures.
  **Model D0 is not the production DE engine family**, and passing checks do not prove
  the theorems — the note awaits independent expert review.

Each script prints per-test `PASS` lines and a summary. `test_energy_balance.py`,
`test_v22.py`, `test_math.py`, and `test_v28.py` run on a bare Python install;
`test_v23.py`/`test_v24.py`/`test_v25.py`/`test_v26.py` import `matplotlib` via the
experiment modules, so install `requirements.txt` first.

## Design principles

- **Physics only.** The engine never optimizes toward homeostasis; it enforces
  conservation and locality and lets outcomes emerge.
- **Everything is audited.** The ledger reconciles `dX = S + G − D − Λ − loss − spill`
  each tick; transport dissipation is non-negative by construction.
- **Impact is counterfactual.** An actor is credited only with the burden it
  demonstrably prevented, not with activity.
