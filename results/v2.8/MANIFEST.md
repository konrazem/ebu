# V2.8 result artifacts — discrete mathematical foundation + numerical validation

**This is a mathematical specification / numerical-validation stage, NOT an engine or
economy change.** No physics or EBU accounting source file is modified. The V2.8
theorems are draft mathematics awaiting independent expert review; `test_v28.py`
validates implementation consistency at tested points and **does not prove any
theorem**.

| Field | Value |
|-------|-------|
| V2.7 baseline (math foundation, frozen) | tag `v2.7.0` → `0c1d10bbc8a483da48a6fb6270f5953514f794e6` |
| Physics + ledger baseline (frozen since V2.5) | tag `v2.5.0` → `f3703d8b00eb0161ce6e98f1e64be60301762cac` |
| Branch | `v2.8-discrete-foundation` |
| Starting commit of this release gate | `6a497e58876e4adfa228838c2ae4d89811b2a6b7` |
| V2.8 math-draft commits | `ca2609d` (draft), `7128f56` (curvature + scope correction), `4cf6fcd` (flux-nullspace + engine-scope gaps) |
| V2.8 test commits | `a978bdc` (`test_v28.py`), `6a497e5` (hardened spectral-solver guards) |
| Release-preparation commit | `9416cfb0450edf97dfa9c43fe16a43c27351d9fd` |
| Python | 3.14.2 (`test_v28.py` and `test_math.py` are stdlib-only) |
| Figure/PDF dependencies | numpy, matplotlib, pillow, reportlab (`requirements.txt`, unchanged) |

**Frozen, NOT modified in V2.8:** `energy_balance.py`, `ebu_v22.py`, `ebu_v23.py`,
`ebu_v24.py`, `ebu_v25.py`, `ebu_v26.py`, all prior tests, and
`Foundation_v2.7_math.md` (physics, EBU accounting, and prior mathematics unchanged).

## Scope (D0 only)

V2.8 derives a **synchronous discrete energy–dissipation inequality for Model D0** —
the frozen-state, simultaneous, **unconstrained**, loss-aware, explicit-Euler
discretisation of the V2.7 Onsager flow — with an explicit finite-step remainder
(Theorem 4.4), a corrected Lipschitz constant `L_V` that **sums simultaneously active
penalty weights** (Assumption 2.5; safe bound `2 max_i[max(α_i,β_i)+χ_i]`), one-edge
(5.1), spectral graph (5.2), active-set (5.5) and state-specific (5.6) step-size
bounds, the flux-nullspace Lemma 5.6a (`SJ = 0 ⇒ J = 0` for Onsager flux), a stock/loss
ledger (8.1), one-tick locality (9.1), and Counterexamples A–E.

**Model D0 is NOT the production engine family.** The DE family (DE-core =
`energy_balance.step`; DE24-family = `ebu_v24.step_v24`, six rules; DE26-forced =
`ebu_v26.forced_tick`) differs by operator splitting, post-drive force state,
loss-blind proposal force (where a force is computed at all), sequential live-state
application, conflict scaling / line search, clipping, and `Δt = 1`. **No D0 theorem
transfers to any DE member** (Assumption 3.4).

### Excluded engine mechanisms (each needs its own framework)

clipping/projection at `0`/`K`; spill at `K`; unmet-demand saturation; hard-reserve
constraints; fixed activation cost `c0`; golden-section / coordinate line search;
sequential live-state transfers; horizon optimisation; global/instantaneous field
solves; ledger incentives / EBU issuance; operator splitting `A(N(·))` with `μ` frozen
at `N(xⁿ)`.

### Open conjectures and proof gaps

1. **Conjecture 5.7 (tightness)** of the active-set / state-specific bounds — open
   (only the pure-quadratic one-edge fixture of Counterexample A is settled).
2. **Driven global behaviour** (multi-step discrete LaSalle analogue) — open.
3. **Splitting error D0 → DE family** (Lie/Strang) — open.
4. **Loss-blind engine force** characterisation under `η < 1` — open.
5. **Constrained (projected) descent** admitting clipping/spill/reserve — open.
6. **θ- and band-aware sharper bounds** — open.
7. From V2.7, still open: **C-1′** (discrete driven bound for B_raw — NOT settled by
   Theorem 4.4, since B_raw is loss-blind, split, sequential, clipped, i.e. not D0)
   and **C-2** (reserve surrogate condition).

## Commands

```bash
git checkout v2.8-discrete-foundation
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt          # only for the PDF build and v23–v26 tests

# prior engine/ledger suite — 48 tests
python3 test_energy_balance.py    # 8
python3 test_v22.py               # 7
python3 test_v23.py               # 4
python3 test_v24.py               # 5
python3 test_v25.py               # 9
python3 test_v26.py               # 15 (+ reruns the 33 prior)

# V2.7 mathematical regression — 8 groups, 34 checks (stdlib only)
python3 test_math.py

# V2.8 numerical validation — 11 groups, 132 checks (stdlib only)
python3 test_v28.py               # captured verbatim in v28_validation.txt

# regenerate the typeset PDF (matplotlib mathtext + reportlab)
python3 make_paper_v28_discrete.py    # -> Foundation_v2.8_discrete.pdf (11 pages)
```

## Test totals (verified for this stage; check counts are harness details, not theorem counts)

| Suite | Count | Runtime deps |
|-------|-------|--------------|
| Prior engine/ledger tests | **48** (8+7+4+5+9+15) | stdlib; v23–v26 need `requirements.txt` |
| V2.7 mathematical regression (`test_math.py`) | **34 checks in 8 groups** | stdlib only |
| V2.8 numerical validation (`test_v28.py`) | **132 checks in 11 groups** | stdlib only |

All pass on Python 3.14.2. **A passing run validates the tested points only; it proves
no theorem.**

## V2.8 validation parameters (declared, not tuned)

| Item | Value |
|------|-------|
| Deterministic seed | `20260726` (printed by the harness) |
| Random graphs | 6 graphs: 4–6 cells; 4–9 distinct directed edges |
| Edge parameter ranges | `M ∈ [0.2, 2.0]`, `θ ∈ [0, 0.1]`, `η ∈ [0.5, 1.0]` |
| Cell parameter ranges | `α, β ∈ [0.3, 2.0]`, `χ ∈ {0} ∪ [0.2, 1.0]`, `L = 5`, `U = 15`, `R ∈ [0, 9]`; states `x ∈ [0, 20]` |
| One-edge sweep | weights `(1,1), (2,0.5), (0.5,2)` × `M ∈ {0.4, 2}` × `η ∈ {0.5, 1}` × `θ ∈ {0, 0.05}` × 3 states × 2 dts = 144 combos per weight table |
| Eigensolver | symmetric Jacobi, validated on diagonal/analytic-2×2/3-cycle fixtures + eigenpair residuals + trace sum; hard guards: convergence, residual ≤ 1e-10·scale, PSD, finite λmax |

### Negative controls (all four fired as required)

1. **Counterexample E:** the former max-form constant `L = 2` permits `Δt = 0.4`, yet
   `V: 10 → 13.84`; corrected `L_V = 4` (bound `0.25`) forbids it. A check asserts the
   summed constant, so restoring the old form fails the suite.
2. **Counterexample A:** `Δt* = 1/(2Mw) = 0.5` equals the Theorem 5.1 bound exactly;
   just-below decreases V, at-threshold leaves V unchanged, just-above strictly
   increases V (`2 → 2.008`); the draft's point `Δt = 0.6` reproduces `V = 3.92`.
3. **Counterexample D:** realized marginals `μ = (−3, −4)` at `η = 0.5`; loss-blind
   force `+1` vs loss-aware `−1`; D0 flux stays zero; executing the loss-blind transfer
   gives `ΔV = +0.010125` (matches first-order prediction `+0.01`).
4. **Sequential locality violation:** synchronous D0 leaves the distance-2 cell
   bit-identical after one tick; a sequential live-state tick leaks `0.0162` to
   distance 2 in one nominal tick.

### Maximum reported numerical residuals (release run)

| Quantity | Value |
|----------|-------|
| `max(|r_n| − R_n)` | `2.442e-15` (fp roundoff at exact-equality fixtures) |
| max descent margin | `7.105e-15` (fp roundoff, within declared tolerance) |
| max exact-identity residual | `7.105e-15` |
| max eigenpair residual | `1.761e-13` |

## Artifact → command mapping

| Artifact | Produced by |
|----------|-------------|
| `Foundation_v2.8_discrete_draft.md` | authored note (source of record) |
| `Foundation_v2.8_discrete.pdf` | `make_paper_v28_discrete.py` (11 pages, typeset via matplotlib mathtext; every page visually inspected) |
| `test_v28.py` | numerical validation of the note (self-contained D0 reference implementation, independent of every engine module) |
| `results/v2.8/v28_validation.txt` | verbatim capture of `python3 test_v28.py` |

## Notes

- **Not tagged.** Per the release procedure, `v2.8.0` is created only as an annotated
  tag at the merge commit on `main` after the PR merges and post-merge CI passes; this
  branch stage creates no tag.
- `CITATION.cff` version bumped `2.7.0 → 2.8.0` (`date-released: 2026-07-26`); git tag
  withheld until post-merge.
- CI (`.github/workflows/tests.yml`) gains a separately named V2.8 validation step;
  no existing step removed or weakened.
- The release-preparation commit hash is recorded below by a follow-up commit (normal
  commit, no amend), because a commit cannot contain its own hash.

## Release-preparation commits (recorded post-hoc)

- `9416cfb0450edf97dfa9c43fe16a43c27351d9fd` — `V2.8 release: package discrete
  mathematical foundation` (PDF generator + PDF, results capture, manifest, README,
  CI step, CITATION bump).
- This manifest-metadata commit (`V2.8 release: record reproducibility metadata`) is
  the immediate follow-up normal commit recording the hash above; no amend was used.
