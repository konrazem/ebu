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

The model was hardened across four generations, each building on the last:

| Version | File | What it adds |
|---------|------|--------------|
| **V2.0** | [energy_balance.py](energy_balance.py) | Foundation: field, burden `B`, marginal potential `μ`, gradient-flow actor law, conflict resolution, counterfactual impact. |
| **V2.2** | [ebu_v22.py](ebu_v22.py) | A conservation **ledger** asserted every tick, plus a **safe** discrete movement law: a transfer executes only if it provably lowers `B` this tick (line-searched size, no overshoot). |
| **V2.3** | [ebu_v23.py](ebu_v23.py) | **Regeneration**: external-flow, logistic, Allee, and finite sources; an `H`-horizon actor that declines an action helping now but harming a regenerative source later. |
| **V2.4** | [ebu_v24.py](ebu_v24.py) | Six **protective harvest rules** on a closed Allee economy, separating genuine ecological foresight from an artifact of the accept/reject architecture. |

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
ecosystem.py            self-sustaining producer/consumer ecosystem experiment
exp_v2*.py              experiment drivers (print tables, write figures)
audit_v231.py           conservation-ledger audit
test_*.py               tests per version
make_paper*.py          render the PDF papers via reportlab
figures/                generated plots (burden vs time, phase maps, heatmaps, …)
*.pdf                   the Foundation papers, V2.1 → V2.4
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
```

Each script prints per-test `PASS` lines and a summary; 24 tests total. The first
two run on a bare Python install; `test_v23.py`/`test_v24.py` import `matplotlib`
via the experiment modules, so install `requirements.txt` first.

## Design principles

- **Physics only.** The engine never optimizes toward homeostasis; it enforces
  conservation and locality and lets outcomes emerge.
- **Everything is audited.** The ledger reconciles `dX = S + G − D − Λ − loss − spill`
  each tick; transport dissipation is non-negative by construction.
- **Impact is counterfactual.** An actor is credited only with the burden it
  demonstrably prevented, not with activity.
