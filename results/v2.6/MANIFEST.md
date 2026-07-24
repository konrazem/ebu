# V2.6 result artifacts — automated adversarial search study

**This is an adversarial-search / falsification study, not an economy.**

| Field | Value |
|-------|-------|
| Baseline commit (`main`, frozen physics + V2.5 ledger) | `8755d697ce1abe789af3d240eb89833adcb89ad5` |
| Baseline tag | `v2.5.0` |
| Branch | `v2.6-adversary` |
| Branch commit (this study) | `31e32f9d25d494e52a9f397ef3fd8353d89598b9` |
| Python | 3.14.2 |
| Dependencies (figures/PDF only; core is stdlib) | numpy, matplotlib, pillow, reportlab (`requirements.txt`) |

Frozen, NOT modified: `energy_balance.py`, `ebu_v22.py`, `ebu_v23.py`, `ebu_v24.py`, `ebu_v25.py`.

## Commands

```bash
git checkout v2.6-adversary
pip install -r requirements.txt
python3 test_v26.py                       # 12 V2.6 tests + 33 prior (45 total)
python3 exp_v26.py > results/v2.6/v26_experiments.txt
python3 make_paper_v26.py                 # -> Energy_Balance_Project_Foundation_v2.6.pdf
```

## Fixed parameters (declared before final runs; not tuned on evaluation seeds)

| Parameter | Value |
|-----------|-------|
| Ledger debits | `lam_L = 0.1` (transport), `lam_F = 1.0` (irreversible extraction) |
| Reserve / penalty | `delta = 3.0`, `chi = 1.0` (reserve `R_i = A_i + delta`, Allee `A = 8`) |
| Beam / red-team | depth `10`, width `40`, tail `20`, quantities `(0.5, 1.0)*q_max`, coalition `[0, 1]` |
| Exploit persistence margin | `1.0` (B_R) at every tail tick |
| Red-team profitability threshold | net EBU `>= 0.5` during search; exploit requires net `> 0` |
| Randomized topology seeds (study C) | `0..11` (12 seeds), 5x5, `src_frac = 0.4`, 30 ticks |
| Red-team fixture | 3x3, centre Allee source (rho=0.3, K=20, A=8), 8 rim consumers (d=0.3), 2 actors (q_max=4) |

Search is deterministic; no randomness is consumed by the beam/red-team (verified by test).
The randomized study (C) draws layouts from `random.Random(seed)` fixed at t=0.

## Artifact → command mapping

| Artifact | Produced by |
|----------|-------------|
| `v26_experiments.txt` | `python3 exp_v26.py` (sections A, B, C) |
| `figures/v26_policies.png` | `exp_v26.py` (A) |
| `figures/v26_random.png` | `exp_v26.py` (C) |
| `Energy_Balance_Project_Foundation_v2.6.pdf` | `make_paper_v26.py` (numbers from `v26_experiments.txt`) |

## Headline outcome

Positive control (naive ledger): the search **rediscovers an exploit** (net EBU +15.35, persistent
harm). Guarded ledger: **no profitable persistent-harm exploit found** within this space/budget.
Caveat: the myopic greedy guarded adversary was net-harmful on 4 of 12 random layouts (harm up to
+592) with positive EBU — a candidate-exploit signal (persistence not verified) and the next
priority. Not a security proof.
