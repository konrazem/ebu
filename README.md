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

### Where this sits on the road to an EBU economy

| Layer | Status |
|-------|--------|
| Physical simulated world (field, sources, transport, storage) | Implemented (V2.0–V2.2) |
| Homeostatic movement rules | Implemented (V2.2–V2.4) |
| Regenerative / Allee / finite sources | Implemented (V2.3) |
| Conservation and loss accounting | Implemented (V2.2) |
| Basic EBU rewards and penalties | Implemented (V2.5) |
| Adversarial reward-gaming tests | Initial hand-written suite (V2.5) |
| Automated/learning adversaries, collusion, laundering | Not implemented (planned V2.6) |
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
ecosystem.py            self-sustaining producer/consumer ecosystem experiment
exp_v2*.py              experiment drivers (print tables, write figures)
audit_v231.py           conservation-ledger audit
test_*.py               tests per version
make_paper*.py          render the PDF papers via reportlab
figures/                generated plots (burden vs time, phase maps, heatmaps, …)
results/v2.4/           frozen result captures + manifest for the v2.4.0 release
*.pdf                   the Foundation papers, V2.1 → V2.5
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
```

Each script prints per-test `PASS` lines and a summary; 33 tests total. The first
two run on a bare Python install; `test_v23.py`/`test_v24.py`/`test_v25.py` import `matplotlib`
via the experiment modules, so install `requirements.txt` first.

## Design principles

- **Physics only.** The engine never optimizes toward homeostasis; it enforces
  conservation and locality and lets outcomes emerge.
- **Everything is audited.** The ledger reconciles `dX = S + G − D − Λ − loss − spill`
  each tick; transport dissipation is non-negative by construction.
- **Impact is counterfactual.** An actor is credited only with the burden it
  demonstrably prevented, not with activity.
