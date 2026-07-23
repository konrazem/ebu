# V2.4 result artifacts

Frozen deterministic result captures for the **`v2.4.0`** release
(commit `4ac7553b63608464fe7afb8f4fb0a97702be42de`).

These are release evidence, not disposable caches: each is the stdout of a
deterministic script at the tagged commit. Re-running the command below at
`v2.4.0` reproduces the file. Regenerating on `main`/later branches may differ
only if the referenced script changed; check the git history of that script.

All runs are on the pure-stdlib engines plus the figure/experiment drivers;
see `requirements.txt` for the (figure-only) dependencies.

| Artifact | Command | Key parameters |
|----------|---------|----------------|
| `v22_experiments.txt` | `python3 experiments_v22.py` | 10×10 checkerboard; models none/gradient/safe; sweep + 200/5000/50000 ticks; inflow sweep; κ=0.02 |
| `v231_audit.txt` | `python3 audit_v231.py` | Clustered/random audit; 30 seeds variance; η∈{0.90,0.95,0.98,1.00}; H∈{1,3,10,30}, radius 2 & 4; n=8/10, 800–1500 ticks |
| `v23_regeneration.txt` | `python3 exp_v23.py` | 8×8 closed Allee economy; A=8, L=4; gradient/safe/horizon H=3,10,30; 1200 ticks; shock ×0.45 at tick 500 |
| `v24_regeneration.txt` | `python3 exp_v24.py` | 8×8 closed Allee economy; six rules (safe, horizon_gate, horizon_opt, threshold_penalty, hard_reserve, penalty_horizon); 1000 ticks; shock at 500; δ=3, χ=1, H=10 |
| `v24_clustered.txt` | `python3 exp_v24_clustered.py` | Randomized paired clustered layouts; n=8, 800 ticks; 20 seeds (6 for horizon_opt); models none/gradient/safe/horizon_gate/horizon_opt |

## Reproduce

```bash
git checkout v2.4.0
pip install -r requirements.txt          # only needed for v23/v24/clustered/audit
python3 experiments_v22.py > results/v2.4/v22_experiments.txt
python3 audit_v231.py       > results/v2.4/v231_audit.txt
python3 exp_v23.py          > results/v2.4/v23_regeneration.txt
python3 exp_v24.py          > results/v2.4/v24_regeneration.txt
python3 exp_v24_clustered.py> results/v2.4/v24_clustered.txt
```

Note: `exp_v24_clustered.py` draws layouts from a seeded `random.Random(seed)`, so
results are deterministic given the seed set; `horizon_opt` uses a coarse grid + one
refinement in the quantity search, so its numbers can shift slightly under a finer
optimiser (qualitative conclusions unchanged).
