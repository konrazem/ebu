# V2.7 result artifacts — mathematical foundation note

**This is a mathematical specification / documentation stage, NOT an engine or economy
change.** No physics or EBU accounting source file is modified.

| Field | Value |
|-------|-------|
| Baseline commit (physics + V2.5 ledger, frozen) | `8755d697ce1abe789af3d240eb89833adcb89ad5` |
| Baseline tag | `v2.5.0` |
| Prior V2.6 study commit (parent of this stage) | `207bfc0` (`v2.6-adversary`) |
| Branch | `v2.7-math-foundation` |
| Branch commit (this stage) | `8d790cf5ffca32ce4cf6dd45b8836476eff870eb` (manifest hash recorded by the immediate follow-up commit) |
| Python | 3.14.2 (core + `test_math.py` are stdlib-only) |
| Figure/PDF dependencies | numpy, matplotlib, pillow, reportlab (`requirements.txt`) |

**Frozen, NOT modified in V2.7:** `energy_balance.py`, `ebu_v22.py`, `ebu_v23.py`,
`ebu_v24.py`, `ebu_v25.py`, `ebu_v26.py` (physics and EBU accounting unchanged).

## Scope

A written mathematical foundation for the existing engine. It derives the local actor
law as gradient flow of a state functional `V_state = B_homeostasis + B_regeneration`
under a dissipation potential `Ψ(J)`, separating three laws — the continuous Onsager
flux (A), its forward-Euler discretisation (`B_raw`), and the engine's gated line
search (`B_safe`) — and proves a continuous-time energy–dissipation theorem
(Theorem 7.1). It **corrects** four earlier informal claims (logistic existence vs.
sustainability; Allee reserve under drive; the loss-aware `η²` descent bound;
frozen-state-only one-hop causality). It proves nothing about the discrete engine
beyond what is stated; `test_math.py` provides numerical regression validation only.

## Commands

```bash
git checkout v2.7-math-foundation
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# prior engine/ledger suite — 48 tests
python3 test_energy_balance.py    # 8
python3 test_v22.py               # 7
python3 test_v23.py               # 4
python3 test_v24.py               # 5
python3 test_v25.py               # 9
python3 test_v26.py               # 15 (+ reruns the 33 prior)

# V2.7 mathematical regression — 8 groups, 34 numerical checks (stdlib only)
python3 test_math.py

# regenerate the typeset PDF (matplotlib mathtext + reportlab)
python3 make_paper_v27_math.py    # -> Foundation_v2.7_math.pdf
```

## Test totals (verified for this stage)

| Suite | Count | Runtime deps |
|-------|-------|--------------|
| Prior engine/ledger tests | **48** (8+7+4+5+9+15) | stdlib; v23–v26 need `requirements.txt` |
| V2.7 mathematical regression (`test_math.py`) | **34 checks in 8 groups** | stdlib only |

All 48 prior tests and all 34 V2.7 checks pass on Python 3.14.2. The check count is a
harness detail, not a count of theorems; a passing run validates tested points only.

## Artifact → command mapping

| Artifact | Produced by |
|----------|-------------|
| `Foundation_v2.7_math.md` | authored note (source of record) |
| `Foundation_v2.7_math.pdf` | `make_paper_v27_math.py` (typeset via matplotlib mathtext) |
| `test_math.py` | numerical regression validation of the note |

## Parameters used in the regression checks (declared, not tuned)

| Check group | Parameters |
|-------------|-----------|
| Logistic fold/basin/flip | `ρ ∈ {0.4, 0.5, 1.5, 2.2, 2.6}`, `K = 20`, `h*(ρ) = ρK/4` |
| Driven Allee reserve | `ρ = 0.6`, `K = 20`, `A = 5`; drives `h,d,λ,κ,s ∈ {0, 0.05, 0.5}` |
| Loss-aware descent bound | weights `α,β ∈ {0.5,1,2}`, `η ∈ {0.5,0.8,0.9,1.0}`; bound `1/[max(α,β)_i + η² max(α,β)_j]` |
| Force gap | `η ∈ {0.5, 0.9, 1.0}` |
| Causality | 3×3 grid, chain 0→1→2, side sinks blocked; perturbation `+0.5` at cell 0 |
| Energy identity (Thm 7.1) | 3-cell path, `M_e = 0.5`, `θ_e = 0.05`, `η_e = 0.9`; `Δt ∈ {10⁻³, 10⁻⁴}` |

## Remaining open conjectures

- **C-1′ (discrete driven bound):** a discrete counterpart of the Theorem 7.1 identity
  for `B_raw` under the mobility bound — open (continuous case now proved).
- **C-2 (reserve surrogate):** V2.4's constant `R_i = A_i + δ_i` dominates the driven
  reserve `x_r` iff `δ_i ≥ x_r − A_i` over the operating envelope — open.

## Notes

- The two earlier V2.7 commits (`47ad4d8` add note, `7e328ba` add tests) were made on
  `v2.6-adversary` and are already present on `origin/v2.6-adversary`. This
  `v2.7-math-foundation` branch was created from that HEAD so it carries the full V2.7
  history; `v2.6-adversary` was **not** rewritten (its V2.7 commits are already pushed,
  so isolating them would require a force-push, which was not performed).
- **Not tagged.** Per instruction, no git tag is created at this stage.
- `CITATION.cff` version field bumped `2.5.0 → 2.7.0` (git tag withheld).
