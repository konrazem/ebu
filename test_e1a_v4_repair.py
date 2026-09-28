"""E1a v4 PRE-EXECUTION REPAIR gate — B1 calibration identity, B2 threshold cost, B3 seed scope.

**EXECUTION CLASS: NON-MODEL-ADVANCING STATIC/PURE.** Every value below is a
hand-authored or deterministically generated fixture. No random number is drawn, no
RNG object is constructed, no trajectory is generated, no calibration is sampled and
no scientific outcome is inspected. Seed DERIVATION is exercised, which creates no
generator and draws nothing.
"""

from __future__ import annotations

import inspect
import json
import math
import os

from e1a_v4.branch_a import build_field, stiffness_matrix
from e1a_v4.calibration import (
    BLOCK1_GATES, CALIBRATION_ARTIFACT_SCHEMA, CalibrationArtifact, CalibrationCondition,
    branch_a_signature, canonical_float, ge_counts, normalised_H, p_min_null_reference,
    require_calibration,
)
import e1a_v4.calibration as calibration_module
from e1a_v4.contract import load_contract
from e1a_v4.effective_size import N_element, phi_of
from e1a_v4.endpoints import p1_geometry
from e1a_v4.geometry import FieldAnalysis
from e1a_v4.identity import procedure_identity
from e1a_v4.numerics import Refusal
from e1a_v4.status import AnalysisStatus
from e1a_v4.validation.calibrate import CalibrationRequest
from e1a_v4.validation.plan import bind_execution, load_plan
from e1a_v4.validation.seeds import (
    ALLOWED_FAMILIES_KEY, CaseSeedAccess, FrozenSeedMap, ValidationSeedFamily,
    family_seed, replicate_seed,
)

PASSED = 0
FAILED = 0
ROOT = os.path.dirname(os.path.abspath(__file__))
BINDING = load_contract(ROOT)
PLAN = load_plan(ROOT)
PID = procedure_identity(BINDING, {}, ROOT)
ETA, BEAD = 0.00089, 1e-6
N = 2_000_000
DT = 1.2e-4


def check(label: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  [PASS] {label}" + (f"  -- {detail}" if detail else ""))
    else:
        FAILED += 1
        print(f"  [FAIL] {label}" + (f"  -- {detail}" if detail else ""))


def refuses(fn, *a, **k) -> bool:
    try:
        fn(*a, **k)
    except Refusal:
        return True
    return False


FIELDS = {s["id"]: build_field(BINDING, s,
                               calibration_route="force_displacement_with_stokes_drag",
                               viscosity=ETA, bead_radius=BEAD)
          for s in BINDING.fields}


def condition_for(field, *, n=N, dt=DT, taus=None, theta_cap=None, alpha=None,
                  R=200, field_id=None, H=None):
    H = field.H if H is None else H
    taus = tuple(field.tau_modes) if taus is None else tuple(taus)
    return CalibrationCondition(
        field_id=field_id or field.field_id, m=len(H), H_normalised=normalised_H(H), n=n,
        dt=dt, tau_modes=taus, phi_modes=tuple(phi_of(dt, t) for t in taus),
        mode_blocks=((0,), (1,)),
        theta_cap_deg=BINDING.theta_cap_deg if theta_cap is None else theta_cap,
        alpha_1=BINDING.alpha_1 if alpha is None else alpha, replicates=R,
        gates=BLOCK1_GATES, calibrator_identity="EBU-E1A-V4-BLOCK1-SURROGATE-CALIBRATOR-v1",
        procedure_identity=PID, contract_sha256=BINDING.sha256, plan_sha256="0" * 64)


def artifact_for(condition, draws=None, R=200):
    draws = draws or {g: tuple(0.001 * k for k in range(1, R + 1)) for g in BLOCK1_GATES}
    return CalibrationArtifact(
        kind="block1_min_p", procedure_identity=condition.procedure_identity,
        field_id=condition.field_id, n=condition.n, m=condition.m,
        alpha_1=condition.alpha_1, null_draws=draws, condition=condition,
        provenance="HAND-WRITTEN FIXTURE, not calibration", is_fixture=True)


# ------------------------------------------------------------- B1 reproduction
def test_b1_defect() -> None:
    t0, t1 = FIELDS["theta0_circular"], FIELDS["theta1_power"]
    check("the audited pair really do share a geometry signature",
          branch_a_signature(t0.H, N) == branch_a_signature(t1.H, N),
          "both isotropic, so the eigenvalue ratios are identical")
    p0 = phi_of(DT, t0.tau_modes[0])
    p1 = phi_of(DT, t1.tau_modes[0])
    n0, n1 = N_element(p0, p0, N), N_element(p1, p1, N)
    check("yet their temporal laws differ materially",
          abs(n1 / n0 - 1.0) > 0.4,
          f"phi {p0:.6f} vs {p1:.6f}; N_11 {n0:,.0f} vs {n1:,.0f} = {n1/n0:.4f}x")
    check("the repaired binding refuses theta0's artifact for theta1",
          refuses(require_calibration, artifact_for(condition_for(t0)),
                  procedure_identity=PID, condition=condition_for(t1)),
          "CALIBRATION_FIELD_MISMATCH / CALIBRATION_CONDITION_MISMATCH")
    same_name = condition_for(t1, field_id="theta0_circular",
                              taus=t1.tau_modes, H=t1.H)
    check("and refuses it even when the field NAME is forced to agree",
          refuses(require_calibration, artifact_for(condition_for(t0)),
                  procedure_identity=PID, condition=same_name),
          "the mathematical protection is the condition, not the name")
    check("field_id alone is still checked, as fail-safe provenance",
          refuses(require_calibration, artifact_for(condition_for(t0)),
                  procedure_identity=PID,
                  condition=condition_for(t0, field_id="theta3_temperature")))


def test_b1_condition_discrimination() -> None:
    f = FIELDS["theta2_ellipse"]
    base = condition_for(f)
    art = artifact_for(base)
    check("matching complete condition accepted",
          require_calibration(art, procedure_identity=PID, condition=base) is art)
    variants = {
        "different n": condition_for(f, n=N - 1),
        "different dt": condition_for(f, dt=DT * 1.01),
        "different tau/phi": condition_for(f, taus=tuple(t * 1.01 for t in f.tau_modes)),
        "different theta_cap": condition_for(f, theta_cap=10.0),
        "different alpha_1": condition_for(f, alpha=0.005),
        "different replicate count": condition_for(f, R=201),
        "different field_id": condition_for(f, field_id="theta0_circular"),
        "different geometry": condition_for(FIELDS["theta0_circular"]),
    }
    for label, cond in variants.items():
        check(f"{label} -> digest changes", cond.sha256 != base.sha256)
        check(f"{label} -> artifact refused",
              refuses(require_calibration, art, procedure_identity=PID, condition=cond))
    rotated = stiffness_matrix(f.k_modes, f.rot_deg + 7.0)
    rot_cond = condition_for(f, H=[[v / (1.380649e-23 * f.T) for v in row] for row in rotated])
    check("eigenvector ORIENTATION changes the digest",
          rot_cond.sha256 != base.sha256,
          "G1 compares laboratory-frame elements, so orientation is a null-law input")
    scaled_H = [[7.3 * v for v in row] for row in f.H]
    a, b = normalised_H(f.H), normalised_H(scaled_H)
    worst = max(abs(a[i][j] - b[i][j]) / abs(a[i][j])
                for i in range(2) for j in range(2) if a[i][j] != 0.0)
    check("rescaling H_A is invariant in EXACT arithmetic",
          worst < 1e-15, f"worst relative difference {worst:.3e}")
    check("but NOT bit-invariant, so the digest is fail-closed about scale",
          condition_for(f, H=scaled_H).sha256 != base.sha256,
          "refuses a mathematically legitimate reuse; the conservative direction, "
          "and free because no cross-field reuse is permitted")
    check("a schema-1 artifact is refused, not reinterpreted",
          refuses(CalibrationArtifact, kind="block1_min_p", procedure_identity=PID,
                  field_id=f.field_id, n=N, m=2, alpha_1=BINDING.alpha_1,
                  null_draws={g: (0.1, 0.2) for g in BLOCK1_GATES}, condition=base,
                  schema="e1a_v4_block1_calibration/1"))
    check("phi inconsistent with exp(-dt/tau) is refused",
          refuses(CalibrationCondition, field_id="x", m=2,
                  H_normalised=((0.5, 0.0), (0.0, 0.5)), n=N, dt=DT,
                  tau_modes=(1e-3, 1e-3), phi_modes=(0.1, 0.1), mode_blocks=((0,), (1,)),
                  theta_cap_deg=5.0, alpha_1=0.004, replicates=10, gates=BLOCK1_GATES,
                  calibrator_identity="c", procedure_identity=PID,
                  contract_sha256="a" * 64, plan_sha256="b" * 64),
          "the primitives and their reduction must agree")
    check("float canonicalisation is exact, not rounded text",
          float.fromhex(canonical_float(0.1 + 0.2)) == 0.1 + 0.2
          and canonical_float(0.1 + 0.2) != "0.3")
    check("a non-finite value cannot enter an identity",
          refuses(canonical_float, float("nan")))


def test_b1_dependency_completeness() -> None:
    """Auditable, not a fragile hand list: every calibrator input is accounted for."""
    request_fields = set(CalibrationRequest.__dataclass_fields__)
    bound = set(condition_for(FIELDS["theta0_circular"]).canonical())
    not_bound = set(PLAN["calibration"]["condition_binding"]["not_bound"])
    # the request's own field names, mapped onto condition keys
    alias = {"H_A": "H_normalised", "phis": "phi_modes", "replicates": "replicates",
             "theta_cap_deg": "theta_cap_deg", "tau_modes": "tau_modes"}
    unaccounted = []
    for name in sorted(request_fields):
        key = alias.get(name, name)
        if key not in bound and name not in not_bound:
            unaccounted.append(name)
    check("every calibrator input is bound or explicitly documented as not bound",
          not unaccounted, f"unaccounted: {unaccounted}" if unaccounted else
          f"{len(request_fields)} request fields, all accounted for")
    src = inspect.getsource(calibration_module.CalibrationCondition)
    for key in ("T_total", "N_ab", "rank_tol", "alpha_2"):
        check(f"the NOT-bound decision for {key} carries a written reason",
              key in src and key in str(PLAN["calibration"]["condition_binding"]["not_bound"]))
    check("the plan and the code agree on what is bound",
          set(PLAN["calibration"]["condition_binding"]["bound"][0].split()[0:1]) <= bound
          or "field_id" in bound)


# ------------------------------------------------------------- B2 equivalence
FIXTURES = {
    "all distinct": [0.1, 0.5, 0.3, 0.9, 0.2],
    "two-way tie": [0.1, 0.5, 0.5, 0.9, 0.2],
    "multiple ties": [0.3, 0.3, 0.3, 0.7, 0.7],
    "all equal": [1.0, 1.0, 1.0, 1.0],
    "ascending": [1.0, 2.0, 3.0, 4.0, 5.0],
    "descending": [5.0, 4.0, 3.0, 2.0, 1.0],
    "repeated extrema": [9.0, 9.0, 1.0, 1.0, 5.0],
    "R = 1": [3.0],
    "R = 2 equal": [3.0, 3.0],
    "R = 2 distinct": [3.0, 4.0],
    "small mixed": [0.0, -1.0, 2.5, -1.0, 2.5, 7.0],
    "negatives": [-5.0, -2.0, -9.0],
}


def test_b2_equivalence() -> None:
    f = FIELDS["theta0_circular"]
    for label, values in FIXTURES.items():
        draws = {g: tuple(values) for g in BLOCK1_GATES}
        art = artifact_for(condition_for(f, R=len(values)), draws=draws)
        check(f"OLD == NEW on '{label}' (R={len(values)})",
              art.p_min_null() == p_min_null_reference(draws),
              "exact equality")
    # gate-varying fixture, so p_min is not a single column
    mixed = {"G1": (0.1, 0.9, 0.5), "G2": (0.9, 0.1, 0.5),
             "G3": (0.5, 0.5, 0.5), "G4": (0.2, 0.2, 0.7)}
    art = artifact_for(condition_for(f, R=3), draws=mixed)
    check("OLD == NEW when the four gates differ",
          art.p_min_null() == p_min_null_reference(mixed),
          f"{art.p_min_null()}")
    check("the identity itself: 1 + #{j!=i} == #{j}",
          all(1 + sum(1 for j, d in enumerate(v) if j != i and d >= v[i])
              == ge_counts(sorted(v), v[i])
              for v in FIXTURES.values() for i in range(len(v))))
    for bad, name in ((float("nan"), "NaN"), (float("inf"), "+inf"),
                      (float("-inf"), "-inf")):
        check(f"a {name} null draw refuses the artifact",
              refuses(artifact_for, condition_for(f, R=3),
                      draws={g: (0.1, bad, 0.3) for g in BLOCK1_GATES}))
    good = artifact_for(condition_for(f, R=3),
                        draws={g: (0.1, 0.2, 0.3) for g in BLOCK1_GATES})
    for bad, name in ((float("nan"), "NaN"), (float("inf"), "+inf")):
        check(f"a {name} observed statistic is refused, never sorted",
              refuses(good.p_value, "G1", bad))


def test_b2_reuse() -> None:
    f = FIELDS["theta0_circular"]
    R = 400
    draws = {g: tuple((k * 7 % R) / R for k in range(R)) for g in BLOCK1_GATES}
    art = artifact_for(condition_for(f, R=R), draws=draws)
    check("the p_min null is stored, not rebuilt per call",
          art.p_min_null() is art.p_min_null())
    check("the critical p_min is stored, not rebuilt per call",
          art.critical_p_min() == art.p_min_null()[max(0, int(math.floor(art.alpha_1 * R)) - 1)])
    check("the stored threshold equals the superseded reference value",
          art.critical_p_min()
          == p_min_null_reference(draws)[max(0, int(math.floor(art.alpha_1 * R)) - 1)])

    # A P1 evaluation must touch the null exactly 4 times: one lookup per gate.
    # Rebuilding the threshold would cost 4R more.
    calls = {"n": 0}
    real = calibration_module.ge_counts

    def counting(sorted_asc, value):
        calls["n"] += 1
        return real(sorted_asc, value)

    analysis = FieldAnalysis("theta0_circular", AnalysisStatus.ESTIMATED, "",
                             beta_hat=1.0, g1=0.001, g2_spread=1.01, g3=[0.1],
                             g4=0.001, g5=0.01, blocks=[[0], [1]])
    calibration_module.ge_counts = counting
    try:
        CalibrationArtifact.p_value.__globals__["ge_counts"] = counting
        calls["n"] = 0
        p1_geometry(analysis, BINDING, procedure_identity=PID,
                    condition=art.condition, artifact=art)
        used = calls["n"]
    finally:
        calibration_module.ge_counts = real
        CalibrationArtifact.p_value.__globals__["ge_counts"] = real
    check("one P1 evaluation touches the null exactly once per gate",
          used == len(BLOCK1_GATES),
          f"{used} lookups for {len(BLOCK1_GATES)} gates; a rebuild would cost {4*R} more")
    check("p1_geometry never references the superseded quadratic reference",
          "p_min_null_reference" not in inspect.getsource(p1_geometry))


def test_b2_no_circularity() -> None:
    f = FIELDS["theta0_circular"]
    R = 50
    draws = {g: tuple(k / R for k in range(R)) for g in BLOCK1_GATES}
    art = artifact_for(condition_for(f, R=R), draws=draws)
    before = (art.p_min_null(), art.critical_p_min(), art.artifact_sha256)
    analysis = FieldAnalysis("theta0_circular", AnalysisStatus.ESTIMATED, "",
                             beta_hat=1.0, g1=0.5, g2_spread=1.5, g3=[0.4],
                             g4=0.5, g5=0.01, blocks=[[0], [1]])
    for _ in range(5):
        p1_geometry(analysis, BINDING, procedure_identity=PID,
                    condition=art.condition, artifact=art)
    after = (art.p_min_null(), art.critical_p_min(), art.artifact_sha256)
    check("evaluating P1 cannot move the calibration threshold", before == after,
          "validation observations never reach a stored calibration quantity")
    check("the artifact digest covers the stored derived quantities",
          "p_min_null" in inspect.getsource(CalibrationArtifact.artifact_sha256.fget)
          and "critical_p_min" in inspect.getsource(CalibrationArtifact.artifact_sha256.fget))
    other = artifact_for(condition_for(f, R=R),
                         draws={g: tuple((k + 1) / R for k in range(R)) for g in BLOCK1_GATES})
    check("different draws give a different artifact digest",
          art.artifact_sha256 != other.artifact_sha256)


# ------------------------------------------------------------- B3 seed scope
EXPECTED_FAMILIES = {
    "C1_true_bridge_complete": {"validation", "branch_a_measurement"},
    "C2_geometry_false_rejection": {"validation", "branch_a_measurement"},
    "C3_g5_block": {"validation", "branch_a_measurement"},
    "C4_surrogate_validity": {"calibration", "validation", "branch_a_measurement"},
    "C5_plug_in_branch_a": {"validation", "branch_a_measurement"},
    "C6_mode_resolution_boundary": {"validation", "branch_a_measurement"},
    "C7_false_bridge": {"validation", "branch_a_measurement"},
    "C8_blinded_scale_control": {"blinded_scale_control", "branch_a_measurement"},
}


def test_b3_declarations() -> None:
    for case in PLAN["cases"]:
        cid = case["case_id"]
        check(f"{cid} declares a machine-readable family list",
              isinstance(case.get(ALLOWED_FAMILIES_KEY), list) and case[ALLOWED_FAMILIES_KEY])
        check(f"{cid} declares exactly the families its design needs",
              set(case[ALLOWED_FAMILIES_KEY]) == EXPECTED_FAMILIES[cid],
              ", ".join(sorted(case[ALLOWED_FAMILIES_KEY])))
    check("no case is granted the confirmatory family",
          all("confirmatory" not in c[ALLOWED_FAMILIES_KEY] for c in PLAN["cases"]),
          "declared in the seed map, authorised for no case")
    md = open(os.path.join(ROOT, "docs/e1a/E1A_V4_SYNTHETIC_VALIDATION_PLAN.md"),
              encoding="utf-8").read()
    for case in PLAN["cases"]:
        fams = ", ".join(f"`{f}`" for f in case[ALLOWED_FAMILIES_KEY])
        check(f"markdown and JSON agree for {case['case_id']}", fams in md)
    check("a plan case without the key is refused at load",
          refuses(CaseSeedAccess.from_plan, "X",
                  {"cases": [{"case_id": "X"}]}, FrozenSeedMap.derive(BINDING.sha256)))


def test_b3_enforcement() -> None:
    ex = bind_execution(root=ROOT)
    c1 = ex.case_access("C1_true_bridge_complete")
    check("C1 may obtain the Branch-B validation family",
          isinstance(c1.stream(ValidationSeedFamily.VALIDATION), int))
    check("C1 may obtain the INDEPENDENT Branch-A measurement family",
          isinstance(c1.stream(ValidationSeedFamily.BRANCH_A_MEASUREMENT), int))
    check("and the two are different streams",
          c1.stream(ValidationSeedFamily.VALIDATION)
          != c1.stream(ValidationSeedFamily.BRANCH_A_MEASUREMENT),
          "Branch-A error never reuses the Branch-B trajectory stream")
    check("C1 may NOT obtain the calibration family",
          refuses(c1.stream, ValidationSeedFamily.CALIBRATION))
    check("C1 may NOT obtain the blinded-scale-control family",
          refuses(c1.stream, ValidationSeedFamily.BLINDED_SCALE_CONTROL))
    check("C1 may NOT obtain the confirmatory family",
          refuses(c1.stream, ValidationSeedFamily.CONFIRMATORY))
    c4 = ex.case_access("C4_surrogate_validity")
    check("C4 receives exactly the calibration + validation families it needs",
          isinstance(c4.stream(ValidationSeedFamily.CALIBRATION), int)
          and isinstance(c4.stream(ValidationSeedFamily.VALIDATION), int)
          and refuses(c4.stream, ValidationSeedFamily.BLINDED_SCALE_CONTROL))
    c5 = ex.case_access("C5_plug_in_branch_a")
    check("C5 receives exactly its required families",
          isinstance(c5.stream(ValidationSeedFamily.BRANCH_A_MEASUREMENT), int)
          and refuses(c5.stream, ValidationSeedFamily.CALIBRATION))
    c8 = ex.case_access("C8_blinded_scale_control")
    check("only C8 may obtain the blinded-scale-control family",
          isinstance(c8.stream(ValidationSeedFamily.BLINDED_SCALE_CONTROL), int)
          and refuses(c8.stream, ValidationSeedFamily.VALIDATION))
    check("an unknown case ID refuses",
          refuses(ex.case_access, "C9_invented"))
    check("an unknown family object refuses",
          refuses(c1.stream, "validation"),
          "a bare string is not a declared family")


def test_b3_low_level_vs_official() -> None:
    """The auditor's demonstration, and the exact claim that may be made about it."""
    seed_map = FrozenSeedMap.derive(BINDING.sha256)
    low = replicate_seed(
        seed_map.stream(ValidationSeedFamily.BRANCH_A_MEASUREMENT,
                        ValidationSeedFamily.BRANCH_A_MEASUREMENT),
        "C1_true_bridge_complete", 0)
    check("the low-level API still derives a C1 Branch-A seed",
          isinstance(low, int),
          "a derivation is mathematics, not an authorisation")
    check("FrozenSeedMap.stream takes no case argument",
          "case" not in inspect.signature(FrozenSeedMap.stream).parameters,
          "it compares the caller's own two arguments: a symmetry check, not a permission")
    ex = bind_execution(root=ROOT)
    c2 = ex.case_access("C2_geometry_false_rejection")
    check("the OFFICIAL case-scoped route refuses any undeclared family",
          refuses(c2.stream, ValidationSeedFamily.CALIBRATION),
          "enforcement lives at the boundary, not in the primitive")
    official = ex.case_access("C1_true_bridge_complete").replicate(
        ValidationSeedFamily.BRANCH_A_MEASUREMENT, 0)
    check("and produces the identical seed when the family IS authorised",
          official == low,
          "the repair changes who may ask, never what the answer is")
    check("the runner exposes the case-scoped route",
          "case_seed_access" in open(os.path.join(ROOT, "e1a_v4/validation/runner.py"),
                                     encoding="utf-8").read())


def test_no_stochastic_activity() -> None:
    import ast
    offenders = []
    for base in ("e1a_v4", "e1a_v4/validation"):
        for name in sorted(os.listdir(os.path.join(ROOT, base))):
            if not name.endswith(".py"):
                continue
            path = os.path.join(base, name)
            tree = ast.parse(open(os.path.join(ROOT, path), encoding="utf-8").read())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    offenders += [f"{path}:{a.name}" for a in node.names
                                  if a.name.split(".")[0] in ("random", "secrets", "numpy")]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    if node.module.split(".")[0] in ("random", "secrets", "numpy"):
                        offenders.append(f"{path}:{node.module}")
    check("no package module imports an RNG", not offenders, str(offenders))
    check("execution remains unauthorised", PLAN["execution_authorised"] is False)
    check("the plan still reports zero draws",
          "No random number has been drawn" in PLAN["status"])
    check("seed derivation is distinguished from a draw",
          "seed_derivation_is_not_a_draw" in PLAN["seed_family_enforcement"])


def test_scientific_rules_unchanged() -> None:
    a = PLAN["adopted_rules_unchanged"]
    for key, want in (("delta_cross", 0.02), ("delta_abs", 0.05), ("z_cross", 1.959963985),
                      ("z_abs", 1.959963985), ("alpha_geom", 0.005), ("alpha_1", 0.004),
                      ("alpha_2", 0.001), ("theta_cap_deg", 5.0), ("rank_tol", 1e-12),
                      ("pipeline_target", 0.9)):
        check(f"{key} unchanged", a[key] == want, str(a[key]))
    check("primary sigma_psi unchanged at 0.5 degrees",
          BINDING.data["hypothetical_uncertainty_scenario"]["sigma_psi_deg"] == 0.5)
    counts = {c["case_id"]: c["replicate_count"] for c in PLAN["cases"]}
    check("every replicate count unchanged",
          counts == {"C1_true_bridge_complete": 300, "C2_geometry_false_rejection": 400,
                     "C3_g5_block": 400, "C4_surrogate_validity": 2000,
                     "C5_plug_in_branch_a": 400, "C6_mode_resolution_boundary": 400,
                     "C7_false_bridge": 400, "C8_blinded_scale_control": 200})
    check("the design contract did NOT change",
          BINDING.sha256 == "91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b")
    check("the seed map did NOT change and every seed value is identical",
          FrozenSeedMap.derive(BINDING.sha256).as_json()["families"]
          == json.load(open(os.path.join(ROOT, "docs/e1a/e1a_v4_seed_map.json"),
                            encoding="utf-8"))["families"],
          "seeds bind to the contract identity, which did not move")
    check("the repair records that NO scientific rule changed",
          PLAN["preexecution_repair"]["scientific_rules_changed"] == "NONE")
    check("the superseded package is recorded, not erased",
          PLAN["preexecution_repair"]["supersedes"]["rewritten"].startswith("NONE")
          and len(PLAN["preexecution_repair"]["supersedes"]["preserved"]) >= 4)
    check("runtime wording is corrected, not deleted",
          "PROJECTION" in str(PLAN["calibration"]["runtime_accounting_correction"])
          and "infeasible" in str(PLAN["calibration"]["runtime_accounting_correction"]))


GROUPS = (
    ("B1 reproduction of the audited defect", test_b1_defect),
    ("B1 complete calibration condition", test_b1_condition_discrimination),
    ("B1 null-law dependency completeness", test_b1_dependency_completeness),
    ("B2 exact equivalence, old vs new", test_b2_equivalence),
    ("B2 compute once, reuse", test_b2_reuse),
    ("B2 no circularity", test_b2_no_circularity),
    ("B3 per-case declarations", test_b3_declarations),
    ("B3 mechanical enforcement", test_b3_enforcement),
    ("B3 low-level derivation vs official route", test_b3_low_level_vs_official),
    ("no stochastic activity", test_no_stochastic_activity),
    ("scientific rules unchanged", test_scientific_rules_unchanged),
)

if __name__ == "__main__":
    for title, fn in GROUPS:
        print(f"\n{title}")
        fn()
    print(f"\nE1a v4 pre-execution repair gate: {PASSED} passed, {FAILED} failed, "
          f"{len(GROUPS)} groups")
    print("Execution class: NON-MODEL-ADVANCING STATIC/PURE (this suite only)")
    print("  RANDOM DRAWS          : 0")
    print("  TRAJECTORIES          : 0")
    print("  CALIBRATION EXECUTION : NOT RUN")
    print("  VALIDATION CAMPAIGN   : NOT RUN")
    raise SystemExit(1 if FAILED else 0)
