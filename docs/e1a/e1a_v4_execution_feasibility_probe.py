#!/usr/bin/env python3
"""E1a v4 — PRE-EXECUTION FEASIBILITY PROBE. NON-MODEL-ADVANCING. NO RNG.

    python3 docs/e1a/e1a_v4_execution_feasibility_probe.py

NOTHING HERE DRAWS A RANDOM NUMBER. `random` is never imported; the only generator
supplied to frozen code is a fixed repeating sequence used to measure arithmetic cost.
No trajectory is generated and no scientific outcome is inspected.

HISTORY. The original form of this probe established the two blockers reported in
`docs/e1a/E1A_V4_SYNTHETIC_VALIDATION_RESULTS.md` and is preserved unaltered at commit
`58388d7ee53debfcc0070284bc926293dceb2cfb`. It ran against the superseded calibration
API and the superseded identities, so it cannot run against the repaired package. This
version keeps the same questions and answers them for the REPAIRED package:

  Q1  which Branch-A error components move the calibration binding, and is the binding
      now complete in BOTH directions?
  Q2  what does the Block-1 threshold actually cost, measured rather than projected?

What changed since the original: the binding is no longer the eigenvalue-ratio
signature but the complete `CalibrationCondition`, and the threshold is no longer
O(R^2)-per-P1-call but O(R log R)-once. What did NOT change: the calibration
ARCHITECTURE question — four locked per-field artifacts, or one per replicate at that
replicate's measured geometry — is still open, and this probe still does not decide it.
"""

from __future__ import annotations

import math
import os
import sys
import time

sys.path.insert(0, ".")

from e1a_v4.branch_a import build_field, stiffness_matrix
from e1a_v4.calibration import (
    CALIBRATION_ARTIFACT_SCHEMA, CalibrationArtifact, branch_a_signature,
    p_min_null_reference, require_calibration,
)
from e1a_v4.effective_size import N_element, phi_of
from e1a_v4.numerics import Refusal
from e1a_v4.validation.calibrate import CalibrationRequest, generate_block1_artifact
from e1a_v4.validation.plan import bind_execution

FAILURES: list[str] = []
K_B = 1.380649e-23


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
print("\n1. frozen identities, as they stand after the pre-execution repair")
binding = bind_execution(root=".")
plan = binding.plan
print(f"  contract           : {binding.binding.sha256}")
print(f"  plan               : {binding.plan_sha256}")
print(f"  seed map           : {binding.seed_map_sha256}")
print(f"  analysis identity  : {binding.analysis_identity}")
print(f"  execution identity : {binding.execution_identity}")
check(binding.binding.sha256
      == "91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b",
      "the design contract did NOT move in the repair")
check(binding.seed_map.master == 13785910525869478477
      and binding.seed_map.families["calibration"] == 6644164099584621674
      and binding.seed_map.families["validation"] == 5088042359768187837
      and binding.seed_map.families["branch_a_measurement"] == 62746336670861162,
      "every seed VALUE is unchanged; the seed-map FILE hash moved because its "
      "derivation documentation gained the job level")
check(binding.analysis_identity
      != "af1177a9d3220f60f78ef738bbee6c925da3ed632b68a9f51830fffe5e985eb4",
      "the analysis identity DID move: calibration.py and endpoints.py changed")
n_samples = int(plan["generating_model"]["branch_b"]["n_samples"])
R_cal = int(plan["calibration"]["replicates"])
check(n_samples == 2_000_000 and R_cal == 50_000, "declared sizes unchanged",
      f"n_samples = {n_samples:,}, R_cal = {R_cal:,}")
check(plan["calibration"]["artifact_schema"] == CALIBRATION_ARTIFACT_SCHEMA,
      "plan and code agree on the artifact schema", CALIBRATION_ARTIFACT_SCHEMA)
check(plan.get("execution_authorised") is False, "execution_authorised is still false")

# --------------------------------------- 2. the binding, in BOTH directions
print("\n2. the calibration binding, tested in both directions")
fields = {s["id"]: build_field(binding.binding, s,
                               calibration_route="force_displacement_with_stokes_drag",
                               viscosity=0.00089, bead_radius=1e-6)
          for s in binding.binding.fields}
dt = float(plan["generating_model"]["branch_b"]["dt_s"])


def request_for(field, *, H=None, field_id=None, taus=None, R=200):
    H = field.H if H is None else H
    # tau must be ordered WITH ascending H eigenvalues, not in declared k order.
    # The adopted modal-pairing invariant refuses the declared order for an
    # anisotropic field, which is exactly the mispairing it exists to catch.
    taus = (tuple(t for _, t in sorted(zip(field.k_modes, field.tau_modes)))
            if taus is None else tuple(taus))
    return CalibrationRequest(
        field_id or field.field_id, H, n_samples,
        tuple(phi_of(dt, t) for t in taus), R, binding.binding.alpha_1,
        binding.binding.theta_cap_deg, binding.analysis_identity,
        binding.binding.sha256, binding.plan_sha256, dt, taus)


def artifact_for(req):
    return CalibrationArtifact(
        kind="block1_min_p", procedure_identity=req.procedure_identity,
        field_id=req.field_id, n=req.n, m=len(req.H_A), alpha_1=req.alpha_1,
        null_draws={g: tuple(0.001 * k for k in range(1, req.replicates + 1))
                    for g in ("G1", "G2", "G3", "G4")},
        condition=req.condition(), provenance="STRUCTURAL FIXTURE", is_fixture=True)


t0, t1 = fields["theta0_circular"], fields["theta1_power"]
print("  TOO WEAK, the audited direction:")
check(branch_a_signature(t0.H, n_samples) == branch_a_signature(t1.H, n_samples),
      "theta0 and theta1 share the superseded geometry signature",
      "both isotropic, so their eigenvalue ratios are identical")
p0, p1 = phi_of(dt, t0.tau_modes[0]), phi_of(dt, t1.tau_modes[0])
r = N_element(p1, p1, n_samples) / N_element(p0, p0, n_samples)
check(abs(r - 1.0) > 0.4, "yet their effective sizes differ materially",
      f"phi {p0:.6f} vs {p1:.6f}; N_11 ratio {r:.4f}")
refused = None
try:
    require_calibration(artifact_for(request_for(t0)),
                        procedure_identity=binding.analysis_identity,
                        condition=request_for(t1).condition())
except Refusal as exc:
    refused = str(exc)
check(refused is not None, "the repaired binding REFUSES that reuse", (refused or "")[:64] + "...")

print("  TOO STRICT, the direction the superseded report described:")
sigma_k = float(binding.binding.data["hypothetical_uncertainty_scenario"]["sigma_k"])
measured = stiffness_matrix((t0.k_modes[0] * (1 + sigma_k), t0.k_modes[1] * (1 - sigma_k)), 0.0)
measured = [[v / (K_B * t0.T) for v in row] for row in measured]
refused = None
try:
    require_calibration(artifact_for(request_for(t0)),
                        procedure_identity=binding.analysis_identity,
                        condition=request_for(t0, H=measured).condition())
except Refusal as exc:
    refused = str(exc)
check(refused is not None,
      "an artifact locked at the NOMINAL geometry is still refused for a MEASURED H_A",
      "unchanged by the repair, and correct: the null law really did move")
print("      -> the calibration ARCHITECTURE question is therefore still OPEN.")
print("         Four locked per-field artifacts, or one per replicate at its own")
print("         measured geometry? A specification decision, not a software defect.")

# --------------------------------------- 3. what the threshold now costs
print("\n3. Block-1 threshold cost, MEASURED at the frozen R_cal")
req = request_for(fields["theta2_ellipse"], R=R_cal)
t = time.perf_counter()
art = generate_block1_artifact(req, FixedSupplier())
build = time.perf_counter() - t
print(f"  generate + finalise one artifact : {build:8.3f} s   MEASURED")
t = time.perf_counter()
for _ in range(10_000):
    art.critical_p_min()
    for gate in ("G1", "G2", "G3", "G4"):
        art.p_value(gate, 0.5)
per_p1 = (time.perf_counter() - t) / 10_000
print(f"  one P1 use of the finalised null : {per_p1*1e6:8.2f} us  MEASURED")
check(art.p_min_null() is art.p_min_null(), "the threshold is stored, never rebuilt")

small = {g: tuple(art.null_draws[g][:1500]) for g in ("G1", "G2", "G3", "G4")}
t = time.perf_counter()
ref = p_min_null_reference(small)
old_small = time.perf_counter() - t
probe = CalibrationArtifact(
    kind="block1_min_p", procedure_identity=binding.analysis_identity,
    field_id="theta2_ellipse", n=n_samples, m=2, alpha_1=binding.binding.alpha_1,
    null_draws=small, condition=request_for(fields["theta2_ellipse"], R=1500).condition(),
    is_fixture=True)
check(probe.p_min_null() == ref,
      "superseded O(R^2) reference and repaired O(R log R) agree EXACTLY",
      f"R = 1500, {len(ref)} values")
print(f"  superseded form at R = 1500      : {old_small:8.3f} s   MEASURED")
print(f"  projected to R = {R_cal:,}         : {old_small*(R_cal/1500)**2:8.1f} s   PROJECTION")

print("\n  campaign arithmetic, from the declared case structure:")
cells = {"C1": 300 * 4, "C2": 400 * 4, "C3": 400 * 4, "C4": 2000 * 4,
         "C5": 400 * 12 * 4, "C6": 400 * 3, "C7": 400 * 4 * 4, "C8": 200 * 4}
total = sum(cells.values())
print(f"    field-replicates, hence P1 evaluations : {total:,}")
print(f"    four locked artifacts                  : {4*build:8.1f} s          PROJECTION")
print(f"    one artifact per field-replicate       : {total*build/3600:8.1f} core-hours PROJECTION")
print(f"      at 14-way parallelism                : {total*build/14/3600:8.1f} hours"
      "      PARALLELISM ASSUMPTION")
print("    Branch-B trajectory generation is EXCLUDED and is the larger term.")
print("    NOT MEASURED END-TO-END: no campaign, calibration or trajectory has run.")

print("\n" + "=" * 78)
if FAILURES:
    print(f"PROBE INCONSISTENT: {len(FAILURES)} expectation(s) did not hold")
    for f in FAILURES:
        print(f"  - {f}")
else:
    print("PRE-EXECUTION POSITION AFTER THE REPAIR")
    print("  the calibration binding is complete in both directions")
    print("  the Block-1 threshold is no longer a binding cost")
    print("  the calibration ARCHITECTURE decision remains OPEN and undecided here")
print("=" * 78)
print("  RANDOM DRAWS          : 0")
print("  TRAJECTORIES          : 0")
print("  CALIBRATION EXECUTION : NOT RUN")
print("  VALIDATION CAMPAIGN   : NOT RUN")
raise SystemExit(1 if FAILURES else 0)
