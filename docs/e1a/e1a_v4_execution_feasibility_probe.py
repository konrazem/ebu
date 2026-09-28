#!/usr/bin/env python3
"""E1a v4 — PRE-EXECUTION FEASIBILITY PROBE. NON-MODEL-ADVANCING. NO RNG.

Run before the first random draw of the authorised synthetic-validation stage.
It establishes, by deterministic inspection and arithmetic only, whether the
frozen package can execute the declared campaign at all.

    python3 docs/e1a/e1a_v4_execution_feasibility_probe.py

NOTHING HERE DRAWS A RANDOM NUMBER. `random` is never imported; the only
generator supplied to frozen code is a fixed repeating sequence used to measure
arithmetic cost. No trajectory is generated, no scientific outcome is inspected
and no calibration artifact produced here is used for any scientific purpose.

The two questions:

  Q1  does the frozen four-artifact calibration architecture admit the Branch-A
      measurement error the adopted design requires?
  Q2  if not, is the only compliant alternative — one calibration artifact per
      replicate at that replicate's own measured geometry — affordable?
"""

from __future__ import annotations

import math
import sys
import time

sys.path.insert(0, ".")

from e1a_v4.branch_a import stiffness_matrix
from e1a_v4.calibration import CalibrationArtifact, branch_a_signature, require_calibration
from e1a_v4.contract import load_contract
from e1a_v4.effective_size import phi_of
from e1a_v4.endpoints import p1_geometry
from e1a_v4.geometry import FieldAnalysis
from e1a_v4.numerics import Refusal
from e1a_v4.status import AnalysisStatus
from e1a_v4.validation.calibrate import CalibrationRequest, generate_block1_artifact
from e1a_v4.validation.plan import bind_execution

K_B = 1.380649e-23
FAILURES: list[str] = []


def check(ok: bool, label: str, detail: str = "") -> None:
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f"  -- {detail}" if detail else ""))
    if not ok:
        FAILURES.append(label)


class FixedSupplier:
    """Deterministic stand-in for a normal generator. NOT RANDOM."""

    PATTERN = (0.30, -0.15, 0.22, -0.05, 0.11, 0.40, -0.33, 0.07, -0.21, 0.18)

    def __init__(self) -> None:
        self.i = 0

    def normal(self, count: int) -> list[float]:
        out = []
        for _ in range(count):
            out.append(self.PATTERN[self.i % len(self.PATTERN)])
            self.i += 1
        return out


# ---------------------------------------------------------------- 1. identities
print("\n1. frozen identities")
binding = bind_execution(root=".")
EXPECTED = {
    "contract": ("91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b",
                 binding.binding.sha256),
    "plan": ("c9168b82c7420ca0edb92da0cb0624f0763958e95893900a35f27c3c97363ae9",
             binding.plan_sha256),
    "seed map": ("28d8b0584b1cd4da0b9a536c8d332d03a116a3f227efaed135297d46aa944d87",
                 binding.seed_map_sha256),
    "analysis identity": ("af1177a9d3220f60f78ef738bbee6c925da3ed632b68a9f51830fffe5e985eb4",
                          binding.analysis_identity),
    "execution identity": ("88037b9b2ac45bad0ab65151ab3f71897eb11bbd782ad09adfb9d0ca5d049837",
                           binding.execution_identity),
}
for name, (want, got) in EXPECTED.items():
    check(want == got, f"{name} matches the reviewed value", got[:16] + "...")

plan = binding.plan
n_samples = int(plan["generating_model"]["branch_b"]["n_samples"])
R_cal = int(plan["calibration"]["replicates"])
check(n_samples == 2_000_000, "declared record length", f"n_samples = {n_samples:,}")
check(R_cal == 50_000, "declared calibration replicates", f"R_cal = {R_cal:,}")
check(len(plan["calibration"]["artifact_filenames"]) == 4,
      "the plan freezes FOUR calibration artifacts, one per field",
      ", ".join(sorted(plan["calibration"]["artifact_filenames"])))
check(plan.get("execution_authorised") is False,
      "execution_authorised is still false at probe time")

# ------------------------------------------------- 2. which Branch-A terms move the signature
print("\n2. does each declared Branch-A error component move the calibration geometry signature?")
print("   (branch_a_signature hashes the EIGENVALUE RATIOS of H_A and n)")
k_nom = (100e-6, 100e-6)                       # theta0_circular
sig_nom = branch_a_signature(stiffness_matrix(k_nom, 0.0), n_samples)

# Declared scenario magnitudes, applied as FIXED +/-1 sigma offsets. Not draws.
sigma_k, sigma_cm, sigma_psi, sigma_T, T0 = 0.0034, 0.0115, 0.5, 0.1, 298.0

cases = [
    ("common-mode scale   sigma_cm = 1.15%",
     [[v * (1 + sigma_cm) for v in row] for row in stiffness_matrix(k_nom, 0.0)], False),
    ("thermometry         sigma_T  = 0.1 K",
     [[v / (1 + sigma_T / T0) for v in row] for row in stiffness_matrix(k_nom, 0.0)], False),
    ("orientation         sigma_psi= 0.5 deg",
     stiffness_matrix(k_nom, sigma_psi), False),
    ("per-mode stiffness  sigma_k  = 0.34% (differential)",
     stiffness_matrix((k_nom[0] * (1 + sigma_k), k_nom[1] * (1 - sigma_k)), 0.0), True),
]
for label, H, expect_move in cases:
    moved = branch_a_signature(H, n_samples) != sig_nom
    check(moved == expect_move, f"{label} -> signature {'MOVES' if moved else 'invariant'}")

# the design's own attribution of sigma_k's differential part
design = open("docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md", encoding="utf-8").read()
check("`sigma_k` differential part | no | no | **yes (G1/G4)**" in design,
      "the adopted design REQUIRES sigma_k's differential part to reach the gates",
      "design section 11 table")
check("| `sigma_psi` | negligible (2nd order) | negligible | **yes, dominant (G3)** |" in design,
      "and sigma_psi to reach G3, so Branch-A error must be REALISED, not merely declared")
check("sqrt(sigma_k^2/m + (sigma_T/T)^2)"
      in str(load_contract(".").data["hypothetical_uncertainty_scenario"]["sigma_fs_formula"]),
      "sigma_psi does not enter sigma_fs, so it can act ONLY through a realised draw")

# ------------------------------------------------- 3. the fail-closed consequence
print("\n3. consequence for a replicate whose H_A carries the declared sigma_k error")
locked = CalibrationArtifact(
    kind="block1_min_p", procedure_identity=binding.analysis_identity,
    field_id="theta0_circular", n=n_samples, m=2, geometry_signature=sig_nom,
    alpha_1=float(binding.binding.alpha_1),
    null_draws={g: tuple(0.01 * i for i in range(20)) for g in ("G1", "G2", "G3", "G4")},
    provenance="STRUCTURAL FIXTURE - not a scientific calibration", is_fixture=True)
measured = stiffness_matrix((k_nom[0] * (1 + sigma_k), k_nom[1] * (1 - sigma_k)), 0.0)

refused = None
try:
    require_calibration(locked, procedure_identity=binding.analysis_identity,
                        H_A=measured, n=n_samples, field_id="theta0_circular")
except Refusal as exc:
    refused = str(exc)
check(refused is not None and "CALIBRATION_IDENTITY_MISMATCH" in refused,
      "require_calibration refuses the measured geometry against the locked artifact",
      (refused or "")[:72] + "...")

analysis = FieldAnalysis(
    "theta0_circular", AnalysisStatus.ESTIMATED, "", S=None, K=None, beta_hat=1.0,
    g1=0.001, g2_spread=1.01, g3=[0.1], g4=0.001, g5=0.01, blocks=[[0], [1]])
phis = (0.99, 0.99)
p1_refused = None
try:
    p1_geometry(analysis, binding.binding, procedure_identity=binding.analysis_identity,
                H_A=measured, n=n_samples, phi_modes=phis, artifact=locked)
except Refusal as exc:
    p1_refused = str(exc)
check(p1_refused is not None, "P1 therefore fails closed for that replicate",
      "no beta, no gate decision, no complete pass")

ok_nominal = p1_geometry(analysis, binding.binding,
                         procedure_identity=binding.analysis_identity,
                         H_A=stiffness_matrix(k_nom, 0.0), n=n_samples,
                         phi_modes=phis, artifact=locked)
check(ok_nominal.name == "P1",
      "the SAME artifact is accepted at the nominal geometry",
      "the refusal is caused by the declared sigma_k error, nothing else")

# ------------------------------------------------- 4. cost of the compliant alternative
print("\n4. cost of the only compliant alternative: one artifact per replicate")
H_probe = [[v / (K_B * T0) for v in row] for row in stiffness_matrix((150e-6, 60e-6), 30.0)]
gamma = 6.0 * math.pi * 0.00089 * 1e-6
phis_probe = tuple(phi_of(float(plan["generating_model"]["branch_b"]["dt_s"]), gamma / k)
                   for k in (150e-6, 60e-6))

R_probe = 2000
req = CalibrationRequest("probe", H_probe, n_samples, phis_probe, R_probe,
                         float(binding.binding.alpha_1), 5.0,
                         binding.analysis_identity, binding.binding.sha256, binding.plan_sha256)
t0 = time.perf_counter()
probe_art = generate_block1_artifact(req, FixedSupplier())
gen_cost = (time.perf_counter() - t0) * R_cal / R_probe
print(f"    generate_block1_artifact   : {gen_cost:8.1f} s at R_cal = {R_cal:,} (linear)")

fits = []
for R in (500, 1000, 2000):
    a = CalibrationArtifact(
        kind="block1_min_p", procedure_identity="P", field_id="probe", n=n_samples, m=2,
        geometry_signature="g", alpha_1=0.004,
        null_draws={g: tuple(probe_art.null_draws[g][:R]) for g in ("G1", "G2", "G3", "G4")},
        is_fixture=True)
    t0 = time.perf_counter()
    a.p_min_null()
    dt = time.perf_counter() - t0
    fits.append(dt * (R_cal / R) ** 2)
    print(f"    p_min_null R = {R:5d}       : {dt:8.3f} s  -> {fits[-1]:9.1f} s at R_cal (quadratic)")
spread = (max(fits) - min(fits)) / min(fits)
check(spread < 0.15, "p_min_null scales as O(R^2), extrapolation is stable",
      f"spread {spread*100:.1f}% across three probe sizes")
per_artifact = gen_cost + sum(fits) / len(fits)
print(f"    => one artifact costs        : {per_artifact:8.1f} s")

FIELD_CELLS = {
    "C1": 300 * 4, "C2": 400 * 4, "C3": 400 * 4, "C4": 2000 * 4,
    "C5": 400 * 12 * 4, "C6": 400 * 3, "C7": 400 * 4 * 4, "C8": 200 * 4,
}
total_cells = sum(FIELD_CELLS.values())
core_seconds = total_cells * per_artifact
print(f"    declared field-replicates    : {total_cells:,}"
      f"   (C5 alone {FIELD_CELLS['C5']:,})")
print(f"    per-replicate calibration    : {core_seconds:,.0f} core-seconds"
      f"  = {core_seconds/86400:,.1f} core-days")
print(f"    at 14-way parallelism        : {core_seconds/14/86400:,.1f} days")
check(core_seconds / 14 / 86400 > 1.0,
      "per-replicate calibration is not affordable", "exceeds one day even 14-way parallel")

# ------------------------------------------------- verdict
print("\n" + "=" * 78)
if FAILURES:
    print(f"PROBE INCONSISTENT: {len(FAILURES)} expectation(s) did not hold")
    for f in FAILURES:
        print(f"  - {f}")
else:
    print("EXECUTION BLOCKED BEFORE FIRST RANDOM DRAW")
    print("  B1  the four locked per-field calibration artifacts do not cover any")
    print("      replicate whose H_A carries the declared sigma_k differential error,")
    print("      which the adopted design REQUIRES in order to reach G1/G4.")
    print("  B2  the compliant alternative, one artifact per replicate at its own")
    print("      measured geometry, is not affordable at the frozen R_cal = 50000.")
print("=" * 78)
print("  RANDOM DRAWS          : 0")
print("  TRAJECTORIES          : 0")
print("  CALIBRATION EXECUTION : NOT RUN")
print("  VALIDATION CAMPAIGN   : NOT RUN")
raise SystemExit(1 if FAILURES else 0)
