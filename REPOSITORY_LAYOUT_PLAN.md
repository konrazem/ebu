# EBP Repository Layout Plan (Gate 0 — design only, no migration)

**Status:** planning document. Nothing is moved, renamed, deleted, or modified by
this gate; the only file this gate adds is this plan. The migration itself is a
separately authorized future stage.

- Audited commit: `6d17f9e01153bd3cc52bc4d7981daab193b720fd`
  (branch `v2.9-local-law-validation`, V2.9 Gate 2 complete).
- Planning branch: `repo-structure-planning` (created from that commit).
- Tracked files audited: **83**.
- Tags verified present and unmoved: `v2.4.0` → `4ac7553`, `v2.5.0` → `f3703d8`,
  `v2.6.0` → `207bfc0`, `v2.7.0` → `0c1d10b`, `v2.8.0` → `05ba912`
  (`v2.5.0`/`v2.7.0`/`v2.8.0` match the values recorded in
  `results/v2.8/MANIFEST.md`).

---

## 1. Current repository inventory (83 tracked files, classified)

### 1.1 Reusable / shared implementation (8)

| File | Notes |
|---|---|
| `energy_balance.py` | V2.0 core engine. Imported by every `ebu_v2x` engine, `ecosystem.py`, `analysis.py`, `audit_v231.py`, all experiment drivers, `test_energy_balance/test_v22..v26/test_math`, and `test_v29.py` (group 11 regeneration cross-check). |
| `ebu_v22.py` | Imports `energy_balance`; `ecosystem` (in `__main__` demo). Imported by `ebu_v23/v24/v25`, `experiments_v22`, `test_v22`, `test_math`. Frozen since v2.5.0. |
| `ebu_v23.py` | Imports `energy_balance`, `ebu_v22`. Imported by `ebu_v24/v25/v26`, `audit_v231`, `exp_v23`, `exp_v24_clustered`, `test_v23/test_v25`. Frozen. |
| `ebu_v24.py` | Imports `energy_balance`, `ebu_v22`, `ebu_v23`. Imported by `exp_v24`, `exp_v24_clustered`, `test_v24/25/26`. Frozen. |
| `ebu_v25.py` | Imports `energy_balance`, `ebu_v22`, `ebu_v23`. Imported by `ebu_v26`, `exp_v25`, `exp_v26`, `test_v25/26`. Frozen. |
| `ebu_v26.py` | Imports `energy_balance`, `ebu_v23`, `ebu_v25`. Imported by `exp_v26`, `test_v26`. Frozen. |
| `d0_v29.py` | V2.9 Stage-A D0 engine (stdlib-only, imports nothing project-local by design — enforced by `test_v29.py` group 9 AST check). Imported by `exp_v29`, `test_v29`, `test_v29_behavior`. Frozen by the V2.9 protocol unless a genuine bug is found. |
| `ecosystem.py` | Shared ecosystem fixture builder. Imports `energy_balance`. Imported by `ebu_v22` (demo), `analysis.py`, `test_v22`. |

### 1.2 Experiment drivers that are ALSO import dependencies (4)

These are experiments by role but are imported as modules by tests or other
scripts, so they cannot be treated as leaf study scripts:

| File | Imported by |
|---|---|
| `experiments_v22.py` | `audit_v231.py` (`make_world`, `stats`) |
| `exp_v23.py` | `test_v23`, `test_v24`, `test_v25`, `exp_v24`, `exp_v25` |
| `exp_v26.py` | `test_v26` |
| `exp_v29.py` | `test_v29_behavior` (imported as `exp`) |

### 1.3 Leaf experiment scripts (6)

`analysis.py` (V2.0/2.1 figures + `ecosystem.gif`), `audit_v231.py` (V2.3.1
ledger audit), `exp_v24.py`, `exp_v24_clustered.py`, `exp_v25.py` — plus
`ecosystem.py`'s demo role (classified above as shared because it is imported).

### 1.4 Tests (10)

`test_energy_balance.py`, `test_v22.py`, `test_v23.py`, `test_v24.py`,
`test_v25.py`, `test_v26.py`, `test_math.py` (V2.7), `test_v28.py` (also the
independent D0 oracle imported by `test_v29.py` and `test_v29_behavior.py`),
`test_v29.py`, `test_v29_behavior.py`.

Critical coupling: `test_v26.py::test_prior_33_pass` re-runs the 33 prior tests
via `importlib.import_module("test_energy_balance")` … `("test_v25")` — the
prior test files must stay importable under those exact module names from the
directory the suite runs in. `test_v29.py` reads `d0_v29.py` and
`test_v29_behavior.py` reads `exp_v29.py` **by relative path** for AST checks.

### 1.5 Protocol / mathematical notes (3)

`Foundation_v2.7_math.md`, `Foundation_v2.8_discrete_draft.md`,
`V2.9_BEHAVIORAL_PROTOCOL_DRAFT.md` (hash-referenced by `exp_v29.py`, which
regex-extracts the Amendment-3 canonical plan hash from it at run time).

### 1.6 Preregistration data (1)

`v29_deterministic_plan.json` — canonical-SHA-256-locked
(`af8f119b4af433290e6fc2546913868421e2f4adcaa467eb6d4d31e5e4856aa2`, recorded in
Amendment 3). Its **content must never change**; moving it is safe, editing is
not.

### 1.7 PDF / paper generators (8)

`make_paper.py` (→ v2.1 PDF), `make_paper_v22.py`, `make_paper_v23.py`,
`make_paper_v24.py`, `make_paper_v25.py`, `make_paper_v26.py`,
`make_paper_v27_math.py`, `make_paper_v28_discrete.py`. All write their PDF to
the CWD by a hardcoded `OUT` name and read figures via hardcoded
`figures/*.png` paths (through PIL/reportlab). Numbers are embedded as
literals (they do not parse results files).

### 1.8 Released papers / PDFs (8)

`Energy_Balance_Project_Foundation_v2.1.pdf` … `_v2.6.pdf`,
`Foundation_v2.7_math.pdf`, `Foundation_v2.8_discrete.pdf`. Release artifacts;
never regenerated during migration (reportlab/matplotlib version drift makes
byte-reproduction impossible in general).

### 1.9 Figures (15 files under `figures/`)

By producing script: `analysis.py` → `B_vs_time`, `viable_vs_time`,
`heatmap_snapshots`, `inflow_sweep`; `experiments_v22.py` → `phase_map`,
`shock_recovery`; `audit_v231.py` → `audit`; `exp_v23.py` → `v23_src_stock`,
`v23_viable`; `exp_v24.py` → `v24_stock`, `v24_viable`; `exp_v24_clustered.py`
→ `v24_clustered`; `exp_v25.py` → `v25_compare`; `exp_v26.py` → `v26_policies`,
`v26_random`. Consumed by the corresponding `make_paper*` generators.
Cross-version use: **`make_paper_v22.py` embeds `figures/heatmap_snapshots.png`,
which is produced by the V2.0/2.1-era `analysis.py`.**

### 1.10 Result captures (10) and reproducibility manifests (4)

`results/v2.4/` (5 captures + `MANIFEST.md`), `results/v2.6/` (1 + manifest),
`results/v2.7/` (manifest only), `results/v2.8/` (1 + manifest),
`results/v2.9/deterministic/` (3 captures: stdout, summary JSON, trace JSON).
All frozen evidence; **never regenerated in place**.

### 1.11 Project / release metadata (6)

`README.md`, `LICENSE`, `CITATION.cff`, `requirements.txt`, `.gitignore`,
`.github/workflows/tests.yml`. CI note: the workflow currently runs the prior
48 tests, `test_math.py`, and `test_v28.py` — it does **not** run `test_v29.py`
or `test_v29_behavior.py` (pre-existing gap to close at the V2.9 release gate,
independent of this plan).

### 1.12 Obsolete / uncertain (1)

`ecosystem.gif` (2.1 MB generated animation, product of `analysis.py`; listed
in the README file map but embedded nowhere). **Uncertain**: keep as historical
artifact (default) or untrack at a version boundary. Flagged as an unresolved
decision (§9).

---

## 2. Proposed target structure

```
.
├── README.md                  # rewritten for the new layout
├── LICENSE
├── CITATION.cff
├── requirements.txt           # kept; pyproject.toml added for packaging
├── pyproject.toml             # NEW: src-layout package + compat alias modules
├── MIGRATION.md               # NEW: layout change log + historical-reproduction note
├── .gitignore
├── .github/workflows/tests.yml
├── docs/                      # high-level docs (this plan archives here post-migration)
│
├── src/ebp/                   # current reusable implementation (installable package)
│   ├── __init__.py            # NEW
│   ├── energy_balance.py
│   ├── ebu_v22.py … ebu_v26.py
│   ├── d0_v29.py
│   ├── ecosystem.py
│   └── experiments/           # experiment drivers that are import dependencies
│       ├── __init__.py        # NEW
│       ├── experiments_v22.py
│       ├── exp_v23.py
│       ├── exp_v26.py
│       └── exp_v29.py
│
├── tests/                     # flat: all test_*.py side by side (see §4)
│   └── test_*.py  (10 files, names unchanged)
│
└── studies/                   # frozen per-version study artifacts
    ├── v2_1/  {experiments,figures,paper}/      # V2.0 core + V2.1 paper era
    ├── v2_2/  {figures,paper}/
    ├── v2_3/  {experiments,figures,paper}/
    ├── v2_4/  {experiments,figures,paper,results}/
    ├── v2_5/  {experiments,figures,paper}/
    ├── v2_6/  {figures,paper,results}/
    ├── v2_7/  {docs,paper,results}/
    ├── v2_8/  {docs,paper,results}/
    └── v2_9/  {docs,results}/
```

Design rules applied:

1. **Graduation rule:** any module imported by another module lives in
   `src/ebp/` (engines, `ecosystem`, and the four test-imported experiment
   drivers). Only leaf scripts and frozen artifacts live in `studies/`.
   Nothing is duplicated.
2. **Frozen vs current:** `studies/` holds frozen historical evidence
   (results, figures, papers, protocols); `src/ebp/` holds importable code.
   "Frozen" is a policy enforced by tests and manifests, not by directory —
   the engine files remain frozen wherever they live.
3. Root is limited to metadata, packaging, CI, and high-level docs.

## 3. Exact old-path → new-path mapping (all 83 tracked files)

Legend for the "dependents to update" column: **imports** = Python import
statements; **CI** = `.github/workflows/tests.yml`; **RM** = README commands or
links; **gen** = paper-generator figure paths; **const** = in-file path
constants.

### Stays at root (6)

| Old path | New path | Dependents to update |
|---|---|---|
| `README.md` | `README.md` | content rewritten (RM) |
| `LICENSE` | `LICENSE` | — |
| `CITATION.cff` | `CITATION.cff` | — |
| `requirements.txt` | `requirements.txt` | CI keeps `pip install -r requirements.txt`; add `pip install -e .` |
| `.gitignore` | `.gitignore` | add `src/ebp/**/__pycache__` etc. as needed |
| `.github/workflows/tests.yml` | same | CI: every `python test_*.py` → `python tests/test_*.py` (run from repo root) |

### Shared implementation → `src/ebp/` (8)

| Old | New | Dependents to update |
|---|---|---|
| `energy_balance.py` | `src/ebp/energy_balance.py` | imports in `ebu_v22..v26`, `ecosystem`, `analysis`, `audit_v231`, `experiments_v22`, `exp_v23/25/26`, `exp_v24_clustered`, `test_energy_balance/v22/v23/v24/v25/v26/math`, `test_v29.py` (group 11); RM code links |
| `ebu_v22.py` | `src/ebp/ebu_v22.py` | imports in `ebu_v23/v24/v25`, `experiments_v22`, `test_v22`, `test_math` (incl. private `_line_search_q`, `_proposals`); RM |
| `ebu_v23.py` | `src/ebp/ebu_v23.py` | imports in `ebu_v24/v25/v26`, `audit_v231`, `exp_v23`, `exp_v24_clustered`, `test_v23/v25` (incl. `_horizon_impact`, `_radius_cells`, `nat_cell`); RM |
| `ebu_v24.py` | `src/ebp/ebu_v24.py` | imports in `exp_v24`, `exp_v24_clustered`, `test_v24/v25/v26`; RM |
| `ebu_v25.py` | `src/ebp/ebu_v25.py` | imports in `ebu_v26`, `exp_v25`, `exp_v26`, `test_v25/v26` (incl. `_action_effect`, `b_plain`, `b_R`); RM |
| `ebu_v26.py` | `src/ebp/ebu_v26.py` | imports in `exp_v26`, `test_v26`; RM |
| `d0_v29.py` | `src/ebp/d0_v29.py` | imports in `exp_v29`, `test_v29`, `test_v29_behavior`; **`test_v29.py:508` `open("d0_v29.py")` AST check (const)**; V2.9-protocol freeze — see §9 |
| `ecosystem.py` | `src/ebp/ecosystem.py` | imports in `ebu_v22` (demo), `analysis`, `test_v22`; RM (`python ecosystem.py` demo command) |

### Import-dependency experiment drivers → `src/ebp/experiments/` (4)

| Old | New | Dependents to update |
|---|---|---|
| `experiments_v22.py` | `src/ebp/experiments/experiments_v22.py` | import in `audit_v231`; FIGDIR const (writes `figures/…` in CWD → target `studies/v2_2/figures/`); RM; `results/v2.4/MANIFEST.md` documents the historical command (manifest NOT edited — tag note instead) |
| `exp_v23.py` | `src/ebp/experiments/exp_v23.py` | imports in `test_v23/v24/v25`, `exp_v24`, `exp_v25`; FIGDIR const → `studies/v2_3/figures/`; RM; v2.4 manifest note |
| `exp_v26.py` | `src/ebp/experiments/exp_v26.py` | import in `test_v26`; FIGDIR const → `studies/v2_6/figures/`; RM; v2.6 manifest note |
| `exp_v29.py` | `src/ebp/experiments/exp_v29.py` | import in `test_v29_behavior` (+ its `open("exp_v29.py")` AST check, const); **`PLAN_PATH`/`PROTOCOL_PATH`/`OUT_DIR` consts** → new `studies/v2_9/` paths (anchor on repo root or `__file__`, keep `load_plan(base_dir)` API); RM |

### Tests → `tests/` (10, filenames unchanged)

| Old | New | Dependents to update |
|---|---|---|
| `test_energy_balance.py`, `test_v22.py`, `test_v23.py`, `test_v24.py`, `test_v25.py`, `test_v26.py`, `test_math.py`, `test_v28.py`, `test_v29.py`, `test_v29_behavior.py` | `tests/<same name>` | CI commands; RM commands; engine/experiment imports become package imports or compat aliases (§5); `test_v26` importlib list works unchanged because peers stay side by side; `test_v29`/`test_v29_behavior` `open(...)` path consts; `test_v29_behavior` reads `exp.PROTOCOL_PATH` (follows the exp const) |

### `studies/v2_1/` — V2.0 core / V2.1 paper era (8)

| Old | New | Dependents to update |
|---|---|---|
| `analysis.py` | `studies/v2_1/experiments/analysis.py` | imports (`energy_balance`, `ecosystem`); FIGDIR const; `ecosystem.gif` output path; RM |
| `make_paper.py` | `studies/v2_1/paper/make_paper.py` | figure paths (gen); `OUT` const; RM |
| `Energy_Balance_Project_Foundation_v2.1.pdf` | `studies/v2_1/paper/…v2.1.pdf` | RM link |
| `ecosystem.gif` | `studies/v2_1/figures/ecosystem.gif` | RM file map; `analysis.py` output path (const) — or untrack (§9) |
| `figures/B_vs_time.png` | `studies/v2_1/figures/B_vs_time.png` | `make_paper.py` (gen) |
| `figures/viable_vs_time.png` | `studies/v2_1/figures/viable_vs_time.png` | `make_paper.py` (gen) |
| `figures/heatmap_snapshots.png` | `studies/v2_1/figures/heatmap_snapshots.png` | `make_paper.py` AND `make_paper_v22.py` (cross-study figure — gen paths in both) |
| `figures/inflow_sweep.png` | `studies/v2_1/figures/inflow_sweep.png` | `make_paper.py` (gen) |

### `studies/v2_2/` (4)

| Old | New | Dependents to update |
|---|---|---|
| `make_paper_v22.py` | `studies/v2_2/paper/make_paper_v22.py` | figure paths incl. cross-study `heatmap_snapshots` (gen); `OUT`; RM |
| `Energy_Balance_Project_Foundation_v2.2.pdf` | `studies/v2_2/paper/…v2.2.pdf` | RM |
| `figures/phase_map.png` | `studies/v2_2/figures/phase_map.png` | `make_paper_v22.py` (gen) |
| `figures/shock_recovery.png` | `studies/v2_2/figures/shock_recovery.png` | `make_paper_v22.py` (gen) |

### `studies/v2_3/` (6)

| Old | New | Dependents to update |
|---|---|---|
| `audit_v231.py` | `studies/v2_3/experiments/audit_v231.py` | imports (`energy_balance`, `ebu_v23`, `experiments_v22`); FIGDIR; RM; v2.4 manifest note |
| `make_paper_v23.py` | `studies/v2_3/paper/make_paper_v23.py` | figure paths (`audit`, `v23_*`) (gen); `OUT`; RM |
| `Energy_Balance_Project_Foundation_v2.3.pdf` | `studies/v2_3/paper/…v2.3.pdf` | RM |
| `figures/audit.png` | `studies/v2_3/figures/audit.png` | `make_paper_v23.py` (gen) |
| `figures/v23_src_stock.png` | `studies/v2_3/figures/v23_src_stock.png` | `make_paper_v23.py` (gen) |
| `figures/v23_viable.png` | `studies/v2_3/figures/v23_viable.png` | `make_paper_v23.py` (gen) |

### `studies/v2_4/` (13)

| Old | New | Dependents to update |
|---|---|---|
| `exp_v24.py` | `studies/v2_4/experiments/exp_v24.py` | imports (`ebu_v24`, `exp_v23`); FIGDIR; RM; v2.4 manifest note |
| `exp_v24_clustered.py` | `studies/v2_4/experiments/exp_v24_clustered.py` | imports; FIGDIR; RM; manifest note |
| `make_paper_v24.py` | `studies/v2_4/paper/make_paper_v24.py` | figure paths (gen); `OUT`; RM |
| `Energy_Balance_Project_Foundation_v2.4.pdf` | `studies/v2_4/paper/…v2.4.pdf` | RM |
| `figures/v24_stock.png` / `v24_viable.png` / `v24_clustered.png` | `studies/v2_4/figures/<same>` | `make_paper_v24.py` (gen) |
| `results/v2.4/MANIFEST.md` | `studies/v2_4/results/MANIFEST.md` | content NOT edited; README/MIGRATION note explains historical commands apply at tag `v2.4.0` |
| `results/v2.4/v22_experiments.txt`, `v231_audit.txt`, `v23_regeneration.txt`, `v24_clustered.txt`, `v24_regeneration.txt` | `studies/v2_4/results/<same>` | never regenerated in place |

### `studies/v2_5/` (4)

| Old | New | Dependents to update |
|---|---|---|
| `exp_v25.py` | `studies/v2_5/experiments/exp_v25.py` | imports (`energy_balance`, `ebu_v25`, `ebu_v23`, `exp_v23`); FIGDIR; RM |
| `make_paper_v25.py` | `studies/v2_5/paper/make_paper_v25.py` | figure path `v25_compare` (gen); `OUT`; RM |
| `Energy_Balance_Project_Foundation_v2.5.pdf` | `studies/v2_5/paper/…v2.5.pdf` | RM |
| `figures/v25_compare.png` | `studies/v2_5/figures/v25_compare.png` | `make_paper_v25.py` (gen) |

### `studies/v2_6/` (6)

| Old | New | Dependents to update |
|---|---|---|
| `make_paper_v26.py` | `studies/v2_6/paper/make_paper_v26.py` | figure paths `v26_*` (gen); `OUT`; RM |
| `Energy_Balance_Project_Foundation_v2.6.pdf` | `studies/v2_6/paper/…v2.6.pdf` | RM |
| `figures/v26_policies.png` / `v26_random.png` | `studies/v2_6/figures/<same>` | `make_paper_v26.py` (gen) |
| `results/v2.6/MANIFEST.md` | `studies/v2_6/results/MANIFEST.md` | not edited; tag note (`v2.6.0`) |
| `results/v2.6/v26_experiments.txt` | `studies/v2_6/results/v26_experiments.txt` | never regenerated in place |

### `studies/v2_7/` (4)

| Old | New | Dependents to update |
|---|---|---|
| `Foundation_v2.7_math.md` | `studies/v2_7/docs/Foundation_v2.7_math.md` | RM links |
| `Foundation_v2.7_math.pdf` | `studies/v2_7/paper/Foundation_v2.7_math.pdf` | RM |
| `make_paper_v27_math.py` | `studies/v2_7/paper/make_paper_v27_math.py` | `OUT` const; RM |
| `results/v2.7/MANIFEST.md` | `studies/v2_7/results/MANIFEST.md` | not edited; tag note (`v2.7.0`) |

### `studies/v2_8/` (5)

| Old | New | Dependents to update |
|---|---|---|
| `Foundation_v2.8_discrete_draft.md` | `studies/v2_8/docs/Foundation_v2.8_discrete_draft.md` | RM links; V2.9 protocol references it by name (prose only, no code read) |
| `Foundation_v2.8_discrete.pdf` | `studies/v2_8/paper/Foundation_v2.8_discrete.pdf` | RM |
| `make_paper_v28_discrete.py` | `studies/v2_8/paper/make_paper_v28_discrete.py` | `OUT` const; RM (its prose cites `results/v2.8/v28_validation.txt` as text — update only if ever re-run) |
| `results/v2.8/MANIFEST.md` | `studies/v2_8/results/MANIFEST.md` | not edited; tag note (`v2.8.0`) |
| `results/v2.8/v28_validation.txt` | `studies/v2_8/results/v28_validation.txt` | never regenerated in place |

### `studies/v2_9/` (5)

| Old | New | Dependents to update |
|---|---|---|
| `V2.9_BEHAVIORAL_PROTOCOL_DRAFT.md` | `studies/v2_9/docs/V2.9_BEHAVIORAL_PROTOCOL_DRAFT.md` | `exp_v29.PROTOCOL_PATH` const; `test_v29_behavior` (via `exp.PROTOCOL_PATH`); RM. Content NOT edited (hash lock reads it). |
| `v29_deterministic_plan.json` | `studies/v2_9/docs/v29_deterministic_plan.json` | `exp_v29.PLAN_PATH` const. **Content byte-frozen** (canonical hash `af8f119b…56aa2`). |
| `results/v2.9/deterministic/v29_deterministic_stdout.txt` | `studies/v2_9/results/deterministic/<same>` | `exp_v29.OUT_DIR` const (for future runs); never regenerated in place |
| `results/v2.9/deterministic/v29_deterministic_summary.json` | `studies/v2_9/results/deterministic/<same>` | as above |
| `results/v2.9/deterministic/v29_deterministic_trace.json` | `studies/v2_9/results/deterministic/<same>` | as above |

New files created by the migration (not moves): `pyproject.toml`,
`src/ebp/__init__.py`, `src/ebp/experiments/__init__.py`, `MIGRATION.md`,
compat alias modules (§5), `docs/` (archived copy of this plan).

---

## 4. Tests: per-study vs central — tradeoff and recommendation

**Option A — per-study (`studies/v2_X/tests/`).** Pro: each study is fully
self-contained; a frozen study carries its own validation. Con: it breaks the
real dependency web — `test_v26.py` imports the five prior test modules by
name and re-runs them (the "48 total" claim depends on it); `test_v29.py` and
`test_v29_behavior.py` import `test_v28.py` as their independent oracle. With
per-study tests these cross-imports need path bootstrapping across eight
directories, and CI needs eight working directories. High breakage risk for
zero functional gain.

**Option B — central `tests/`, one flat directory (recommended).** All ten
files keep their names side by side. `python3 tests/test_v26.py` works because
Python puts the script's directory on `sys.path`, so `importlib.import_module
("test_v22")` and `import test_v28` resolve unchanged. Version grouping is
already carried by the filenames. Sub-folders (`tests/core/`, `tests/v2_2/`…)
were considered and rejected: they reintroduce exactly the cross-directory
import problem of Option A while adding nothing the filenames don't already
express.

**Recommendation: Option B (flat central `tests/`).**

---

## 5. Compatibility strategy

1. **Packaging.** Add `pyproject.toml` (setuptools, src-layout): package `ebp`
   from `src/`. CI and dev environments run `pip install -e .` once; all
   engines become importable as `ebp.<module>` from any CWD.
2. **Intra-package imports.** Engine-to-engine imports (`from energy_balance
   import …` inside `ebu_v2x`) are rewritten to package-relative form
   (`from ebp.energy_balance import …`). This edits import lines of files
   declared frozen — an explicit authorization item (§9 R1); semantics are
   verified byte-identical by the full suite and scratch-diff of deterministic
   outputs (§8).
3. **Temporary compat alias modules** (removal target: one release after
   migration). Installed with the package (a `compat/` module set declared in
   `pyproject.toml`), one per historical top-level module name:
   `energy_balance`, `ebu_v22`…`ebu_v26`, `d0_v29`, `ecosystem`,
   `experiments_v22`, `exp_v23`, `exp_v26`, `exp_v29`. Each does
   `from ebp.<module> import *` **plus explicit re-export of the private names
   imported across the codebase** (`_line_search_q`, `_proposals`,
   `_horizon_impact`, `_radius_cells`, `nat_cell`, `_action_effect`,
   `b_plain`, `b_R`, `step_v25`, …), because `import *` skips underscore
   names. With aliases installed, the ten test files run **without editing
   their import statements**, and user scripts written against the old flat
   layout keep working with a deprecation note in MIGRATION.md.
4. **Path constants.** CWD-relative constants are updated where the owning
   file moves: `exp_v29.PLAN_PATH`/`PROTOCOL_PATH`/`OUT_DIR` (anchored on the
   repo root via `__file__` so the hash lock and result paths are
   CWD-independent), `test_v29.py:508` (`open("d0_v29.py")` → the new engine
   path), `test_v29_behavior.py:663` (`open("exp_v29.py")` → new path), every
   `FIGDIR`, every `make_paper*` figure path and `OUT`. These touch two files
   the V2.9 protocol froze (`d0_v29.py` is only moved, not edited;
   `test_v29.py` needs its one `open()` literal changed) — timing and
   authorization in §9/§10.
5. **Historical commands.** Manifests are never edited. `MIGRATION.md` + a
   README section state: *to reproduce a tagged release, check out its tag —
   the manifest's commands are valid at that tag's layout.* Tags are never
   moved, so every recorded hash remains reachable and truthful.
6. **CI.** Same test list (plus, at the V2.9 release gate, the currently
   missing `test_v29.py` and `test_v29_behavior.py`), run from repo root as
   `python tests/test_X.py`, after `pip install -r requirements.txt` and
   `pip install -e .`.

---

## 6. Staged migration sequence

Each stage is one commit on a dedicated `repo-structure-migration` branch,
gated on the full verification block (§8). No stage begins until the previous
one is green.

- **S0 — baseline (no repo change).** Record current outputs of all ten suites
  and `pip freeze` to a scratch directory; verify tags; verify
  `exp_v29`'s hash lock passes.
- **S1 — scaffolding (additive only).** Add `pyproject.toml`,
  `src/ebp/__init__.py` (empty package doc), `tests/` `.gitkeep`-free stub is
  unnecessary — create dirs implicitly at S2/S3; add `MIGRATION.md`. Suites
  still run from root unchanged.
- **S2 — shared code.** `git mv` the 8 shared modules + 4 driver modules into
  `src/ebp/`(+`/experiments`); rewrite intra-package imports; add compat alias
  modules; `pip install -e .`; full verification. Root keeps no engine copies
  (aliases are installed, not tracked at root).
- **S3 — tests + CI.** `git mv` the ten test files to `tests/`; update the two
  literal `open()` paths and `exp_v29` path constants; update
  `.github/workflows/tests.yml`; full verification (run exactly the CI block
  locally).
- **S4 — studies.** `git mv` papers, generators, figures, protocols, plan
  JSON, and results per §3; update `FIGDIR`/`OUT`/figure-path constants in
  generators and leaf experiments; full verification + hash-lock re-check +
  `git diff` proof that every moved results/plan file is a pure rename
  (`git diff --find-renames --name-status` shows `R100`).
- **S5 — docs.** Rewrite README (file map, commands, links); archive this plan
  under `docs/`; final full verification.
- **S6 (later release, after one cycle) — remove compat aliases** and update
  test imports to `ebp.*` in the same commit, with identical check counts.

Merge to `main` only after S5, by PR, with tags untouched.

---

## 7. Rollback strategy

- One commit per stage → rollback of stage *k* is `git revert <stage-k-sha>`
  (revert, never force-push, once the branch is pushed).
- Before the branch is pushed/shared, a failed stage may instead be dropped by
  resetting the local branch to the previous stage tip.
- The migration branch is disposable until merged; the scientific branches and
  every tag are untouched throughout, so the ultimate rollback is simply not
  merging.
- Because all moves are `git mv` (pure renames, `R100`), `git log --follow`
  preserves file history either way.

---

## 8. Verification block (run after every stage)

```bash
git status --short                 # expect: clean after commit
git diff --check                   # no whitespace damage
git diff --find-renames --name-status HEAD~1  # moves are R100 renames, results byte-identical

pip install -r requirements.txt && pip install -e .   # from S2 onward

python3 tests/test_energy_balance.py   # 8      (root paths before S3)
python3 tests/test_v22.py              # 7
python3 tests/test_v23.py              # 4
python3 tests/test_v24.py              # 5
python3 tests/test_v25.py              # 9
python3 tests/test_v26.py              # 15 (+ reruns the 33 prior)
python3 tests/test_math.py             # 34 checks / 8 groups
python3 tests/test_v28.py              # 132 checks / 11 groups
python3 tests/test_v29.py              # 141 checks / 15 groups
python3 tests/test_v29_behavior.py     # 108 checks / 9 groups

# result captures: regenerate to SCRATCH ONLY and diff (never in place);
# byte-comparison is only meaningful on the interpreter that produced the
# frozen capture (3.14.2 for v2.8/v2.9 captures)
python3 src/ebp/experiments/exp_v29.py > /tmp/scratch_v29_stdout.txt  # after S4 path update
diff /tmp/scratch_v29_stdout.txt studies/v2_9/results/deterministic/v29_deterministic_stdout.txt

# V2.9 hash lock still verifies against the moved protocol + plan
python3 - <<'EOF'
from ebp.experiments import exp_v29
plan, h = exp_v29.load_plan()
assert h == "af8f119b4af433290e6fc2546913868421e2f4adcaa467eb6d4d31e5e4856aa2"
print("hash lock OK")
EOF

for t in v2.4.0 v2.5.0 v2.6.0 v2.7.0 v2.8.0; do git rev-parse "$t^{}"; done  # unchanged
grep -oE '\]\([^)]+\)' README.md      # spot-check that linked paths exist (S5)
```

Expected totals remain exactly: prior 48 (8+7+4+5+9+15), V2.7 34/8, V2.8
132/11, V2.9 conformance 141/15, V2.9 behavior 108/9.

---

## 9. Risks and unresolved decisions

- **R1 (authorization required): frozen-file import edits.** `ebu_v22–v26`
  (frozen since v2.5.0/v2.8.0 statements), `d0_v29.py`/`test_v29.py` (frozen
  by the V2.9 protocol) need import-line or path-literal edits. Position:
  freezes protect *semantics and evidence*; edits are mechanical, verified by
  identical check counts and scratch diffs, and historical bytes stay
  reachable at the tags. Must be explicitly authorized in the migration gate
  and called out in MIGRATION.md; `test_v29.py` edits additionally require
  rerunning the full V2.8/V2.9 cross-conformance per the V2.9 protocol.
- **R2: hidden module-name coupling.** `test_v26.py` imports prior test
  modules by name; compat aliases must re-export every private name actually
  imported (`test_math` imports `_line_search_q`; `test_v25` imports
  `_action_effect`, …). Mitigation: grep-driven alias generation + full suite.
- **R3: CWD-relative reads.** `test_v29.py` (`open("d0_v29.py")`),
  `test_v29_behavior.py` (`open("exp_v29.py")`), `exp_v29`
  (plan/protocol/results paths), all `FIGDIR`/`OUT` constants. Every one is
  enumerated in §3; missing even one breaks a suite or writes output to a
  wrong directory. Mitigation: §8 block runs every suite and a scratch
  experiment rerun.
- **R4: stdout byte-comparison is interpreter-sensitive.** Frozen captures
  were made on Python 3.14.2; CI uses 3.12. Scratch diffs are performed only
  on a matching interpreter; CI relies on check counts instead.
- **R5: PDFs are not byte-reproducible** (reportlab/matplotlib drift). Papers
  are moved, never regenerated; generators are updated only so a *deliberate*
  future re-run works.
- **R6: cross-study figure.** `make_paper_v22.py` embeds the v2.1-era
  `heatmap_snapshots.png`; its new path crosses studies
  (`../../v2_1/figures/…`). Accepted and documented rather than duplicating
  the figure.
- **R7 (unresolved): `ecosystem.gif`** — keep under `studies/v2_1/figures/`
  (default) or untrack to shrink the repo. Owner decision at migration time.
- **R8 (unresolved): package name.** Plan assumes `ebp` (matches project
  name); repository slug is `ebu`. Decide before S1; all §5 examples update
  mechanically.
- **R9 (pre-existing, independent):** CI does not run `test_v29.py` /
  `test_v29_behavior.py`; fix belongs to the V2.9 release gate, not this
  migration, but S3 should not accidentally "fix" it silently — add it
  deliberately at the release gate (per the project release checklist).
- **R10: history discoverability.** After moves, README/MIGRATION must state
  that pre-migration paths live at the tags; `git log --follow` covers
  per-file history.

---

## 10. When to migrate (recommendation)

**After the V2.9 study is complete — merged and tagged `v2.9.0` — and before
any V3.0 scientific work begins.** Reasons:

1. V2.9 is an *active preregistered study*: its protocol freezes `d0_v29.py`
   and `test_v29.py` and hash-locks the plan/protocol pair that `exp_v29.py`
   reads by path. Moving those mid-study forces frozen-file edits inside a
   running scientific gate — exactly the kind of change preregistration is
   meant to prevent.
2. After `v2.9.0` exists, every historical reproduction path goes through a
   tag, so layout churn on `main` carries no reproducibility cost.
3. The migration then lands as a dedicated engineering-only stage (no
   scientific claims), with the full suite as its acceptance test, before new
   science starts accumulating on the old layout.

Interim (now → v2.9.0): no structural changes; new V2.9 artifacts keep
following the existing conventions (`results/v2.9/…`, root modules).

## 11. Files that remain at repository root (post-migration)

`README.md`, `LICENSE`, `CITATION.cff`, `requirements.txt`, `pyproject.toml`
(new), `MIGRATION.md` (new, temporary until archived), `.gitignore`,
`.github/` — nothing else. All code, tests, studies, results, figures, papers
and protocols live under `src/`, `tests/`, `studies/`, `docs/`.
