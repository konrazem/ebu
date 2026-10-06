"""E1a V-stage PROCEDURE VERSION 6 -- core repair regressions.

One test family per blocker the independent V5 audit left open:

A. the numerical sensitivity certification is actually guaranteed;
B. the axial remainder set is derived over U's joint 99.9% physical region;
C. the official C_phi path carries every required calibration primitive;
D. the 0.0005 absolute and contrast bias ceilings are enforced predicates;
E. observation qualification is in detector coordinates and pre-Branch-B;
F. gate-calibration provenance is a verifiable receipt, not a string;
G. both negative controls exercise their controlling validation obligations.

Nothing here runs a confirmatory campaign, consumes a confirmatory seed or
uses physical data.
"""

from __future__ import annotations

import io
import math
import os
import tokenize
from decimal import Decimal
from fractions import Fraction

from e1a_v5 import certified as cert
from e1a_v5 import numerics as nm
from e1a_v5.calibration import (
    REQUIRED_PRIMITIVE_CATEGORIES,
    CategoryDeclaration,
    CertifiedSensitivity,
    JOINT_REGION_NONCOVERAGE,
    PrimitiveClass,
    SensitivityFailure,
    build_joint_region,
    certified_inverse_norm,
    certified_profiled_sensitivity,
)
from e1a_v5.confidence import (
    BIAS_ABS_MAX,
    BIAS_CONTRAST_MAX,
    CEILING_PASS,
    CEILING_UNRESOLVED,
    SIGMA_CAL_ABS_MAX,
    SIGMA_CAL_CONTRAST_MAX,
)
from e1a_v5.evidence import (
    GATE_DIGEST_MISMATCH,
    GATE_FIXTURE_IN_PRODUCTION,
    GATE_NOT_A_RECEIPT,
    GateCalibrationReceipt,
    GateFamily,
    GateLimit,
    SyntheticGateFixture,
    synthetic_calibrated_gate_fixture,
)
from e1a_v5.generate import (
    AxialMemorySpec,
    ResponseSpec,
    axial_memory_dynamics,
    exact_semigroup_residual,
    generate_response_record,
)
from e1a_v5.observation import (
    LOCALIZATION_RATIO_CEILING,
    ObservationEnvelope,
    generalized_relaxation_rates,
    localization_ratio,
    observed_signal_covariance,
    qualify_observation_envelope,
)
from e1a_v5.reduction import (
    AxialEvidence,
    RemainderSet,
    exact_geometry_effect,
    exact_log_beta_bias,
    remainder_impacts,
    remainder_set_effects,
    schur_complement,
)
from e1a_v5.rng import Stream
from e1a_v5.seeds import (
    CONFIRMATORY_FAMILIES,
    ENGINEERING,
    ENGINEERING_V4,
    ENGINEERING_V5,
    FAMILIES_V2,
    FAMILIES_V3,
    FAMILIES_V4,
    FAMILIES_V5,
    ROOT,
    ROOT_V2,
    ROOT_V3,
    ROOT_V4,
    ROOT_V5,
    SeedMap,
)
from e1a_v5.units import K_B
from e1a_v5.validation import plan
from e1a_v5.validation.cases import ALL_CASES, CASES_BY_ID, ExpectedEvent
from e1a_v5.validation.contract import (
    COMPARED_FIELDS,
    check_correspondence,
    load_plan,
    plan_identity,
    require_correspondence,
)
from e1a_v5.validation.dispatch import instantiate
from e1a_v5.validation.harness import (
    TEMPORAL_QUALIFIED,
    TEMPORAL_UNQUALIFIED,
    auxiliary_measurement,
    axial_effects,
    axial_memory_specs,
    calibration_inputs,
    design_evidence,
    design_log_beta_range,
    design_specs,
    experiment_calibration,
    observation_envelope,
    temporal_qualification,
    true_system,
)
from e1a_v5.validation.run import (
    DOMAIN_IDENTITY,
    NO_GATE_RECEIPTS,
    PROCEDURE_VERSION,
    deterministic_controls,
    gate_expectations,
)

PASSED = 0
FAILED = 0


def check(label: str, ok: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if ok:
        PASSED += 1
    else:
        FAILED += 1
        print(f"  [FAIL] {label} {detail}")


def close(a: float, b: float, tol: float = 1e-12) -> bool:
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def _raises(fn) -> bool:
    try:
        fn()
    except Exception:
        return True
    return False


def _code_lines(path: str):
    """Executable lines only: no comments and no docstrings."""
    with open(path, "rb") as fh:
        src = fh.read()
    drop_c, drop_s = set(), set()
    prev = None
    for tok in tokenize.tokenize(io.BytesIO(src).readline):
        if tok.type == tokenize.COMMENT:
            drop_c.add(tok.start[0])
        if tok.type == tokenize.STRING and (
            prev is None or prev.type in (tokenize.ENCODING, tokenize.INDENT,
                                          tokenize.NEWLINE, tokenize.NL,
                                          tokenize.DEDENT)
        ):
            drop_s.update(range(tok.start[0], tok.end[0] + 1))
        if tok.type not in (tokenize.NL, tokenize.COMMENT):
            prev = tok
    out = []
    for i, line in enumerate(src.decode("utf-8").splitlines(), 1):
        if i in drop_s:
            continue
        if i in drop_c:
            line = line.split("#", 1)[0]
        if line.strip():
            out.append((i, line))
    return out


def _body(path: str) -> str:
    return "".join(l for _, l in _code_lines(path))


# ===========================================================================
# BLOCKER A -- the numerical certification is guaranteed, not assumed
# ===========================================================================

def test_a_no_library_transcendental_in_the_certified_path() -> None:
    """The enclosure may not rest on an undocumented libm property."""
    body = _body(os.path.join("e1a_v5", "certified.py"))
    start = body.index("def _atanh_enclosure")
    end = body.index("def isqrt")
    region = body[start:end]
    for forbidden in ("math.log(", "math.exp(", ".ln(", ".exp(", "math.log10"):
        check(f"the certified series never calls {forbidden!r}",
              forbidden not in region)
    check("the declared route uses no library transcendental",
          cert.TRANSCENDENTAL_BACKEND["library_transcendentals_used"] == [])
    check("the borrowed guarantee is a SPECIFIED arithmetic property",
          "correctly rounded" in cert.TRANSCENDENTAL_BACKEND["arithmetic_guarantee"]
          and "Decimal Arithmetic" in
          cert.TRANSCENDENTAL_BACKEND["arithmetic_guarantee"])
    check("both directed rounding modes are declared",
          set(cert.TRANSCENDENTAL_BACKEND["directed_rounding"])
          == {"ROUND_FLOOR", "ROUND_CEILING"})


def test_a_exact_input_conversion() -> None:
    """A float enters the certified path as its EXACT binary value."""
    body = _body(os.path.join("e1a_v5", "certified.py"))
    check("no decimal display string is ever parsed",
          "Decimal(str(" not in body and "Decimal(repr(" not in body)
    for x in (0.1, 1e-300, 3.141592653589793, 1.0 - 2.0 ** -53):
        check(f"Decimal({x!r}) is the exact binary value",
              Fraction(Decimal(x)) == Fraction(x))
    # frexp / ldexp range reduction is exact in binary.
    for x in (0.1, 1e100, 1e-100, 7.0):
        m, e = math.frexp(x)
        check(f"frexp on {x!r} is exact", Fraction(m) * Fraction(2) ** e == Fraction(x))


def test_a_transcendental_enclosures() -> None:
    """Every returned interval encloses the true value, on a wide battery."""
    # The reference is a 120-digit decimal evaluation, NOT the platform libm:
    # the certified enclosure is tighter than libm near x = 1, so testing
    # against libm would reject correct answers.
    from decimal import localcontext

    def ref_log(x: float) -> Decimal:
        with localcontext() as ctx:
            ctx.prec = 120
            return Decimal(x).ln()

    def ref_exp(x: float) -> Decimal:
        with localcontext() as ctx:
            ctx.prec = 120
            return Decimal(x).exp()

    xs = [2.0 ** k for k in range(-60, 61)]
    xs += [1.0 + 10.0 ** -k for k in range(1, 16)]
    xs += [0.1, 0.5, 1.0, 2.718281828459045, 1e-300, 1e300]
    worst = 0.0
    tighter_than_libm = 0
    for x in xs:
        lo, hi = cert.ilog((x, x))
        ref = ref_log(x)
        check(f"log enclosure contains the value at {x!r}",
              Decimal(lo) <= ref <= Decimal(hi), f"{lo!r} {ref} {hi!r}")
        if lo <= math.log(x) <= hi:
            tighter_than_libm += 1
        worst = max(worst, (hi - lo) / max(abs(float(ref)), 1.0))
    check("log enclosures are tight", worst < 1e-14, repr(worst))
    # A CROSS-CHECK, explicitly not the basis of the certification: the
    # platform libm agrees with the certified series everywhere tested.  If it
    # ever did not, the certified series would still be the answer.
    check("the platform libm agrees with the certified series",
          tighter_than_libm == len(xs), f"{tighter_than_libm}/{len(xs)}")
    worst = 0.0
    for x in [k * 0.5 for k in range(-200, 200)] + [1e-8, -1e-8, 0.0, 700.0]:
        lo, hi = cert.iexp((x, x))
        ref = ref_exp(x)
        check(f"exp enclosure contains the value at {x!r}",
              Decimal(lo) <= ref <= Decimal(hi), f"{lo!r} {ref} {hi!r}")
        worst = max(worst, (hi - lo) / float(ref))
    check("exp enclosures are tight", worst < 1e-14, repr(worst))
    # Monotone endpoints: an interval input maps to the interval of outputs.
    lo, hi = cert.ilog((1.5, 2.5))
    check("log maps endpoints to endpoints",
          lo <= math.log(1.5) and math.log(2.5) <= hi)
    check("log of a possibly non-positive interval refuses",
          _raises(lambda: cert.ilog((-1.0, 1.0))))


def test_a_sqrt_is_proved_not_assumed() -> None:
    """``isqrt`` proves its endpoints by exact rational comparison."""
    body = _body(os.path.join("e1a_v5", "certified.py"))
    start = body.index("def isqrt")
    region = body[start:body.index("def ilog")]
    check("isqrt verifies with exact rational arithmetic", "Fraction(" in region)
    for x in (2.0, 1e-300, 1e300, 0.1, 1.0, 1.0000000000000002):
        lo, hi = cert.isqrt((x, x))
        check(f"sqrt lower endpoint is PROVED at {x!r}",
              Fraction(lo) * Fraction(lo) <= Fraction(x))
        check(f"sqrt upper endpoint is PROVED at {x!r}",
              Fraction(hi) * Fraction(hi) >= Fraction(x))
    check("sqrt of a possibly negative interval refuses",
          _raises(lambda: cert.isqrt((-1.0, 1.0))))


def test_a_hyper_dual_operations_carry_every_order() -> None:
    """Every operation in the certified chain enclosed to second order."""
    x = cert.IHD.seed(1.7, 1.0, 0.0)
    y = cert.IHD.seed(2.3, 0.0, 1.0)
    # d2(xy)/dx dy = 1 exactly.
    check("product mixed second derivative is exact",
          (x * y).d12[0] <= 1.0 <= (x * y).d12[1])
    # d2 (x/y) / dx dy = -1/y^2
    q = x / y
    check("quotient mixed second derivative is enclosed",
          q.d12[0] <= -1.0 / (2.3 ** 2) <= q.d12[1])
    # single-variable second derivatives, seeded on both slots
    for fn, second in (
        (lambda v: v.log(), lambda v: -1.0 / (v * v)),
        (lambda v: v.exp(), lambda v: math.exp(v)),
        (lambda v: v.sqrt(), lambda v: -0.25 / (v ** 1.5)),
    ):
        z = cert.IHD.seed(1.7, 1.0, 1.0)
        got = fn(z)
        want = second(1.7)
        check("second derivative enclosed", got.d12[0] <= want <= got.d12[1],
              f"{got.d12} vs {want}")


def test_a_riccati_value_and_derivative_fixed_points() -> None:
    """The VALUE and every DERIVATIVE component carry their own bound."""
    from e1a_v5.validation.harness import _field_model_builders, _record_indices
    from e1a_v5.packets import RECORDS
    vector, builders = calibration_inputs({})
    key, bf, bg = builders[0]
    base = bf(vector.values)
    truth = cert.gbuild_state_space(
        base.a_drift, base.sigma, [0.0, 0.0], base.p_matrix, base.r_obs,
        list(base.b_det), base.dt, base.t_exp)
    from e1a_v5.calibration import ThetaScaling, truth_matching_theta, _second_partial
    theta0 = truth_matching_theta(base)
    sc = ThetaScaling.for_model(base, theta0)
    res = _second_partial(bg, truth, theta0, sc, vector.values, 0, 0, None,
                          [p.sigma for p in vector.primitives])
    check("four Riccati bounds are reported", len(res.riccati_bounds) == 4)
    check("every Riccati bound is finite and nonnegative",
          all(math.isfinite(b) and b >= 0.0 for b in res.riccati_bounds),
          str(res.riccati_bounds))
    check("the derivative bounds are reported separately from the value",
          res.riccati_derivative_bound >= 0.0
          and res.riccati_mixed_bound >= 0.0)
    check("the Lyapunov tail is bounded too",
          all(math.isfinite(b) and b >= 0.0 for b in res.lyapunov_bounds))
    scale = nm.max_abs(base.sigma)
    check("the fixed-point bounds are far below the covariance scale",
          max(res.riccati_bounds) < 1e-6 * scale, str(res.riccati_bounds))


def test_a_fixed_point_bounds_enter_the_enclosure() -> None:
    """Inflating the proved bound must WIDEN the result, not just report it."""
    from e1a_v5.calibration import ThetaScaling, truth_matching_theta, _second_partial
    vector, builders = calibration_inputs({})
    key, bf, bg = builders[0]
    base = bf(vector.values)
    truth = cert.gbuild_state_space(
        base.a_drift, base.sigma, [0.0, 0.0], base.p_matrix, base.r_obs,
        list(base.b_det), base.dt, base.t_exp)
    theta0 = truth_matching_theta(base)
    sc = ThetaScaling.for_model(base, theta0)
    sig = [p.sigma for p in vector.primitives]
    narrow = _second_partial(bg, truth, theta0, sc, vector.values, 0, 0, None, sig)
    width_narrow = narrow.value.d12[1] - narrow.value.d12[0]
    saved = cert.contraction_bounds
    try:
        cert.contraction_bounds = lambda r, l: tuple(
            1e6 * v for v in saved(r, l))
        wide = _second_partial(bg, truth, theta0, sc, vector.values, 0, 0, None, sig)
        width_wide = wide.value.d12[1] - wide.value.d12[0]
    finally:
        cert.contraction_bounds = saved
    check("a larger fixed-point bound widens the returned enclosure",
          width_wide > width_narrow, f"{width_wide!r} vs {width_narrow!r}")


def test_a_contraction_is_verified_over_the_enclosure() -> None:
    """The contraction constant is bounded on the ball, not at a midpoint."""
    body = _body(os.path.join("e1a_v5", "certified.py"))
    check("an epsilon-inflation acceptance test is present",
          "BALL_INFLATION" in body and "ginflate_matrix(p, claimed)" in body)
    check("a non-contractive map refuses rather than returning a number",
          all(not math.isfinite(b) for b in
              cert.contraction_bounds((1.0, 0.0, 0.0, 0.0),
                                      (1.5, 0.0, 0.0, 0.0))))
    # Graded-norm bookkeeping: every weight is valid, so the minimum is valid.
    b = cert.contraction_bounds((1e-16, 1e-16, 1e-16, 1e-16),
                                (0.1, 0.1, 0.1, 0.1))
    check("a contractive map yields finite bounds in every component",
          all(math.isfinite(v) and v > 0.0 for v in b), str(b))


def test_a_certified_linear_solve() -> None:
    """Nonsingularity is PROVED by interval Cholesky, not estimated."""
    body = _body(os.path.join("e1a_v5", "calibration.py"))
    check("the Weyl-plus-backward-error estimate is gone",
          "eig_backward_error" not in body)
    check("the residual is accumulated in interval arithmetic",
          "cert.iadd(" in body and "cert.imul(" in body)
    a = [[2.0, 0.3], [0.3, 1.5]]
    rad = [[0.0, 0.0], [0.0, 0.0]]
    inv_norm, lam = certified_inverse_norm(a, rad)
    vals, _ = nm.eigh(a)
    check("the certified eigenvalue bound is a genuine LOWER bound",
          0.0 < lam <= min(vals) + 1e-12, f"{lam!r} vs {min(vals)!r}")
    check("the inverse norm is its reciprocal", close(inv_norm, 1.0 / lam))
    # Negative definite is fine (the expected information is concave).
    neg = [[-2.0, -0.3], [-0.3, -1.5]]
    inv2, lam2 = certified_inverse_norm(neg, rad)
    check("a negative definite information is certified too", lam2 > 0.0)
    # Indefinite and nearly singular must refuse.
    check("an indefinite information refuses",
          _raises(lambda: certified_inverse_norm([[1.0, 0.0], [0.0, -1.0]], rad)))
    big = [[0.5, 0.5], [0.5, 0.5]]
    check("a singular information refuses",
          _raises(lambda: certified_inverse_norm(big, rad)))
    wide = [[1.0, 0.0], [0.0, 1.0]]
    check("an enclosure wide enough to contain a singular matrix refuses",
          _raises(lambda: certified_inverse_norm(wide, [[2.0, 2.0], [2.0, 2.0]])))


def test_a_failure_semantics_are_fail_closed() -> None:
    """An uncertifiable sensitivity makes the qualification UNRESOLVED."""
    u = CertifiedSensitivity.uncertified(5, "no transcendental enclosure")
    check("an uncertified sensitivity is marked", not u.certified)
    check("its radii are infinite", all(math.isinf(r) for r in u.log_beta_radius))
    check("it records why", "transcendental" in u.failure)
    cal = experiment_calibration()
    broken = type(cal)(**{**cal.__dict__,
                          "sensitivities": (u,) + cal.sensitivities[1:]})
    check("one uncertified row makes the absolute qualification UNRESOLVED",
          broken.absolute_qualification(cal.keys[0]) == CEILING_UNRESOLVED)
    check("and the contrast qualification UNRESOLVED",
          broken.contrast_qualification(cal.keys[1], cal.keys[0])
          == CEILING_UNRESOLVED)
    check("no sensitivities at all is UNRESOLVED, not PASS",
          type(cal)(**{**cal.__dict__, "sensitivities": ()})
          .absolute_qualification(cal.keys[0]) == CEILING_UNRESOLVED)


def test_a_reference_derivatives_are_contained() -> None:
    """The four exact references lie inside the certified intervals."""
    cal = experiment_calibration()
    s = cal.sensitivities[0]
    names = list(cal.phi_names)
    mu_x_row = 1
    for name, row, want in (
        (plan.PRIMITIVE_K_STANDARD, 0, -1.0),
        (plan.PRIMITIVE_T_STANDARD, 0, +1.0),
        (plan.PRIMITIVE_B_DET_X, 0, 0.0),
        (plan.PRIMITIVE_B_DET_X, mu_x_row, -1.0),
    ):
        k = names.index(name)
        got, rad = s.jacobian[row][k], s.radius[row][k]
        check(f"d theta[{row}] / d {name} contains {want}",
              got - rad <= want <= got + rad, f"{got!r} +- {rad!r}")
    check("the 0.009 ceiling is resolved on a certified enclosure",
          cal.absolute_qualification(cal.keys[0]) == CEILING_PASS,
          str(cal.absolute_sigma(cal.keys[0])))
    check("the 0.003 contrast ceiling is resolved too",
          cal.contrast_qualification(cal.keys[1], cal.keys[0]) == CEILING_PASS,
          str(cal.contrast_sigma(cal.keys[1], cal.keys[0])))


# ===========================================================================
# BLOCKER B -- the joint 99.9% physical region
# ===========================================================================

def test_b_joint_region_is_complete_and_covered() -> None:
    region = plan.default_joint_region()
    check("every required category is declared exactly once",
          sorted(c.category for c in region.categories)
          == sorted(REQUIRED_PRIMITIVE_CATEGORIES))
    check("the guaranteed joint coverage is at least 99.9%",
          region.joint_coverage >= 0.999, repr(region.joint_coverage))
    check("the allocated noncoverage is the declared budget",
          close(region.total_noncoverage, JOINT_REGION_NONCOVERAGE))
    check("the coverage basis is the union bound, valid under dependence",
          "union bound" in region.as_dict()["construction"])
    check("the declared latent structure is retained in the region",
          plan.LATENT_THERMOMETRY in region.latent_basis)
    check("bounded systematics are kept apart from the statistical region",
          region.bounded_systematic("wall_hydrodynamic_resistance") > 0.0)
    check("an undeclared bounded systematic is MISSING, not zero",
          _raises(lambda: region.bounded_systematic("detector_offset")))
    check("the region has a construction identity",
          len(region.identity()) == 64)


def test_b_region_construction_refuses_incomplete_declarations() -> None:
    vector = plan.primitive_vector()
    cats = list(plan.category_declarations())
    check("a complete declaration builds", build_joint_region(vector, cats) is not None)
    check("a missing category refuses",
          _raises(lambda: build_joint_region(vector, cats[1:])))
    check("a duplicated category refuses",
          _raises(lambda: build_joint_region(vector, cats + [cats[0]])))
    bad = [c for c in cats if c.category != "shared_standards"]
    bad.append(CategoryDeclaration("shared_standards", PrimitiveClass.UNCERTAIN, ()))
    check("an UNCERTAIN category with no members refuses",
          _raises(lambda: build_joint_region(vector, bad)))
    bad2 = [c for c in cats if c.category != "wall_hydrodynamic_resistance"]
    bad2.append(CategoryDeclaration("wall_hydrodynamic_resistance",
                                    PrimitiveClass.BOUNDED_SYSTEMATIC))
    check("a BOUNDED_SYSTEMATIC with no bound refuses",
          _raises(lambda: build_joint_region(vector, bad2)))
    bad3 = [c for c in cats if c.category != "shared_standards"]
    bad3.append(CategoryDeclaration("shared_standards", PrimitiveClass.EXACT_CONSTANT,
                                    justification=""))
    check("an EXACT_CONSTANT with no justification refuses",
          _raises(lambda: build_joint_region(vector, bad3)))
    check("a primitive no category claims refuses",
          _raises(lambda: build_joint_region(
              vector,
              [c for c in cats if c.category != "detector_offset"]
              + [CategoryDeclaration("detector_offset", PrimitiveClass.NOT_APPLICABLE,
                                     justification="claimed by nothing")])))
    check("over-allocated noncoverage refuses",
          _raises(lambda: build_joint_region(vector, cats, noncoverage=0.5)))


def test_b_remainder_set_is_built_over_the_region() -> None:
    body = _body(os.path.join("e1a_v5", "validation", "plan.py"))
    check("the informal 3 sigma coverage constant is gone",
          "REMAINDER_COVERAGE_K" not in body)
    rs = plan.remainder_set(plan.nominal_k3(0))
    check("the set records the joint region it was built over",
          "joint" in rs.source and "0.999" in rs.source, rs.source)
    check("the radius is positive and inside the SPD domain",
          0.0 < rs.rho < 1.0 and rs.within_domain, repr(rs.rho))
    region = plan.default_joint_region()
    check("the region half-width exceeds a marginal 3 sigma",
          region.coverage_factor[0] > 3.0, repr(region.coverage_factor[0]))
    # Monotone in the region: a wider region cannot give a smaller set.
    wide = build_joint_region(plan.primitive_vector(), plan.category_declarations(),
                              noncoverage=1e-6)
    check("a tighter noncoverage allocation gives a LARGER certified set",
          plan.remainder_set(plan.nominal_k3(0), wide).rho > rs.rho)


def test_b_exact_suprema_survive_over_the_corrected_set() -> None:
    """The cleared formulas, reverified on the region-derived radius."""
    for fidx in range(4):
        rs = plan.remainder_set(plan.nominal_k3(fidx))
        eff = remainder_set_effects(rs, d=2)
        rho = rs.rho
        check(f"field {fidx}: scale supremum is -log(1-rho)",
              close(eff.log_beta_bias, -math.log1p(-rho), 1e-14))
        check(f"field {fidx}: geometry supremum is artanh(rho) at d=2",
              close(eff.geometry, 0.5 * (math.log1p(rho) - math.log1p(-rho)), 1e-14))
        check(f"field {fidx}: centre effect is multiplicative sqrt(1+rho)",
              close(eff.centre_factor, math.sqrt(1.0 + rho), 1e-14))
        check(f"field {fidx}: rate effect is 1+rho",
              close(eff.rate_factor, 1.0 + rho, 1e-14))
        # The supremum must dominate every sampled member of the set.
        for s0 in (-1.0, -0.5, 0.0, 0.5, 1.0):
            for s1 in (-1.0, -0.5, 0.0, 0.5, 1.0):
                e = [[rho * s0, 0.0], [0.0, rho * s1]]
                check(f"field {fidx}: supremum dominates a member",
                      abs(exact_log_beta_bias(e)) <= eff.log_beta_bias + 1e-15
                      and exact_geometry_effect(e) <= eff.geometry + 1e-15)


def test_b_auditor_counterexamples_still_fail() -> None:
    e_scale = [[-0.0004999, 0.0], [0.0, -0.0004999]]
    exact = abs(exact_log_beta_bias(e_scale))
    check("the auditor's scale counterexample is reproduced",
          close(exact, 0.00050002499, 1e-7), repr(exact))
    check("the exact scale effect FAILS the 0.0005 budget", exact > BIAS_ABS_MAX)
    check("the first-order surrogate would have PASSED it",
          0.0004999 <= BIAS_ABS_MAX)
    e_geom = [[0.048752, 0.0], [0.0, -0.048752]]
    g = exact_geometry_effect(e_geom)
    check("the auditor's geometry counterexample is reproduced",
          close(g, 0.048790679067, 1e-9), repr(g))
    check("the exact geometry effect FAILS log 1.05",
          g >= 0.04879016416943205)
    check("a traceless remainder still has a nonzero EXACT scale effect",
          abs(exact_log_beta_bias([[0.02, 0.0], [0.0, -0.02]])) > 1e-5)


def test_b_centre_and_rate_use_the_generalized_construction() -> None:
    """Anisotropic drag enters through lambda(K, Gamma), not a scalar."""
    k = nm.mat([[2.0e-4, 0.0], [0.0, 1.0e-4]])
    iso = nm.scale(nm.eye(2), 1.0e-8)
    aniso = nm.mat([[0.5e-8, 0.0], [0.0, 1.0e-8]])
    r_iso = generalized_relaxation_rates(k, iso)
    r_an = generalized_relaxation_rates(k, aniso)
    check("isotropic drag reproduces K / gamma",
          close(max(r_iso), 2.0e-4 / 1.0e-8, 1e-10))
    check("anisotropic drag widens the relaxation-rate range",
          max(r_an) > max(r_iso), f"{max(r_an)!r} vs {max(r_iso)!r}")
    body = _body(os.path.join("e1a_v5", "observation.py"))
    check("the envelope uses the generalized rates",
          "generalized_relaxation_rates(self.k_eff, self.gamma)" in body)


# ===========================================================================
# BLOCKER C -- the complete C_phi
# ===========================================================================

def test_c_every_required_primitive_category_is_accounted_for() -> None:
    cats = {c.category: c for c in plan.category_declarations()}
    check("fifteen required categories", len(REQUIRED_PRIMITIVE_CATEGORIES) == 15)
    for name in REQUIRED_PRIMITIVE_CATEGORIES:
        check(f"category {name} is declared", name in cats)
        c = cats[name]
        check(f"category {name} has an explicit classification",
              isinstance(c.classification, PrimitiveClass))
        check(f"category {name} declares no defects", c.validate() == [])
    vector = plan.primitive_vector()
    check("the primitive vector carries every uncertain member",
          all(any(p.name == m for p in vector.primitives)
              for c in cats.values()
              if c.classification is PrimitiveClass.UNCERTAIN
              for m in c.members))
    check("absence cannot mean zero uncertainty: every primitive is claimed",
          build_joint_region(vector, plan.category_declarations()) is not None)


def test_c_j_beta_covers_every_stochastic_primitive() -> None:
    cal = experiment_calibration()
    s = cal.sensitivities[0]
    names = list(cal.phi_names)
    check("the primitive basis is much larger than V5's three",
          len(names) >= 25, str(len(names)))
    for name in (plan.PRIMITIVE_P_GAIN, plan.PRIMITIVE_P_SHEAR,
                 plan.PRIMITIVE_R_OBS, plan.PRIMITIVE_B_DET_X,
                 plan.PRIMITIVE_T_EXP, plan.PRIMITIVE_DT,
                 plan.PRIMITIVE_AXIAL_STIFFNESS, plan.PRIMITIVE_AXIAL_COUPLING,
                 plan.PRIMITIVE_BEAD_RADIUS, plan.PRIMITIVE_FORCE_CAL):
        check(f"{name} is in the official primitive basis", name in names)
        k = names.index(name)
        check(f"{name} is not a structural zero", k not in s.structural_zeros)
    for name in (plan.PRIMITIVE_P_GAIN, plan.PRIMITIVE_R_OBS,
                 plan.PRIMITIVE_T_EXP, plan.PRIMITIVE_DT,
                 plan.PRIMITIVE_AXIAL_STIFFNESS, plan.PRIMITIVE_AXIAL_COUPLING,
                 plan.PRIMITIVE_BEAD_RADIUS, plan.PRIMITIVE_FORCE_CAL):
        k = names.index(name)
        check(f"{name} has a nonzero log-beta sensitivity",
              abs(s.log_beta_row[k]) > 0.0, f"{s.log_beta_row[k]!r}")


def test_c_structural_zeros_are_demonstrated() -> None:
    """A zero row is allowed only when the zero is DEMONSTRATED."""
    from e1a_v5.calibration import _primitive_enters
    vector, builders = calibration_inputs({})
    key, bf, bg = builders[0]
    phi = vector.values
    sig = [p.sigma for p in vector.primitives]
    names = [p.key for p in vector.primitives]
    for name in (plan.PRIMITIVE_ETA_REF, plan.PRIMITIVE_ETA_DT,
                 plan.PRIMITIVE_FIDUCIAL_X, plan.PRIMITIVE_FIDUCIAL_Y):
        k = names.index(name)
        check(f"{name} provably does not enter the analysis model",
              not _primitive_enters(bg, phi, k, sig))
    check("a primitive that DOES enter is detected",
          _primitive_enters(bg, phi, names.index(plan.PRIMITIVE_K_STANDARD),
                            phi_scale=sig))
    # And the structural claim is re-derived numerically, not trusted.
    from e1a_v5.calibration import ThetaScaling, truth_matching_theta, _second_partial
    base = bf(phi)
    truth = cert.gbuild_state_space(
        base.a_drift, base.sigma, [0.0, 0.0], base.p_matrix, base.r_obs,
        list(base.b_det), base.dt, base.t_exp)
    theta0 = truth_matching_theta(base)
    sc = ThetaScaling.for_model(base, theta0)
    k = names.index(plan.PRIMITIVE_ETA_REF)
    res = _second_partial(bg, truth, theta0, sc, phi, 0, None, k, sig)
    lo, hi = res.value.d12
    check("the numerically evaluated zero row encloses zero",
          lo <= 0.0 <= hi, str(res.value.d12))
    check("and is zero to far below any budget", max(abs(lo), abs(hi)) < 1e-6,
          str(res.value.d12))
    # The STRUCTURAL argument is the exact one: a numerical evaluation can
    # only bound the zero, because the Riccati fixed-point inflation widens
    # every component including one that is identically zero.  The structural
    # route proves it instead.


def test_c_shared_covariance_is_structural() -> None:
    """A shared standard is ONE latent variable, not an asserted number."""
    v = plan.primitive_vector(share_thermometry=True)
    c = v.covariance()
    i = v.index_of(plan.PRIMITIVE_K_STANDARD)
    j = v.index_of(plan.PRIMITIVE_T_STANDARD)
    rho = c[i][j] / math.sqrt(c[i][i] * c[j][j])
    check("the declared correlation is realised exactly",
          close(rho, plan.ETA_T_CORRELATION, 1e-12), repr(rho))
    check("the latent basis is declared",
          plan.LATENT_THERMOMETRY in v.latents)
    indep = plan.primitive_vector(share_thermometry=False)
    ci = indep.covariance()
    check("the misspecified analyser has no covariance there",
          ci[i][j] == 0.0)
    check("but the same declared variances", close(ci[i][i], c[i][i])
          and close(ci[j][j], c[j][j]))
    check("a loading set exceeding the declared sigma refuses",
          _raises(lambda: v.load_on_latent(plan.PRIMITIVE_K_STANDARD,
                                           plan.LATENT_THERMOMETRY, 2.0)))
    # C_b,cal keeps the off-diagonal blocks the sharing produces.
    cal = experiment_calibration()
    off = cal.c_b_cal[0][1]
    check("shared standards couple the endpoints", abs(off) > 0.0)


def test_c_observation_primitives_reach_the_inference() -> None:
    """Qualifying P, R_obs, the offset, the shutter and timing is not enough."""
    cal = experiment_calibration()
    names = list(cal.phi_names)
    s = cal.sensitivities[0]
    total = cal.absolute_sigma(cal.keys[0]).point
    # Removing the observation primitives must shrink sigma: they contribute.
    obs_names = (plan.PRIMITIVE_P_GAIN, plan.PRIMITIVE_P_SHEAR,
                 plan.PRIMITIVE_R_OBS, plan.PRIMITIVE_T_EXP, plan.PRIMITIVE_DT,
                 plan.PRIMITIVE_BEAD_RADIUS)
    row = list(s.log_beta_row)
    for n in obs_names:
        row[names.index(n)] = 0.0
    without = math.sqrt(sum(
        row[i] * cal.c_phi[i][j] * row[j]
        for i in range(len(row)) for j in range(len(row))))
    check("observation calibration uncertainty really propagates",
          without < total, f"{without!r} vs {total!r}")


# ===========================================================================
# BLOCKER D -- the bounded-bias ceilings are enforced predicates
# ===========================================================================

def test_d_bias_ceilings_are_enforced() -> None:
    body = _body(os.path.join("e1a_v5", "validation", "run.py"))
    check("the absolute bias ceiling is compared in the record builder",
          "BIAS_ABS_MAX" in body)
    check("the contrast bias ceiling is compared in the contrast builder",
          "BIAS_CONTRAST_MAX" in body)
    check("both ceilings are 0.0005",
          BIAS_ABS_MAX == 0.0005 and BIAS_CONTRAST_MAX == 0.0005)


def test_d_design_point_bias_is_reported_honestly() -> None:
    """The design point is UNQUALIFIED on bounded bias.  It is not retuned."""
    worst_abs = 0.0
    for fidx in range(4):
        eff = axial_effects(fidx)
        worst_abs = max(worst_abs, plan.BIAS_PER_CELL + eff.log_beta_bias)
    check("the design point's absolute bounded bias exceeds 0.0005",
          worst_abs > BIAS_ABS_MAX, repr(worst_abs))
    worst_con = 0.0
    for fidx in (1, 2, 3):
        worst_con = max(worst_con, 2.0 * plan.BIAS_PER_CELL
                        + axial_effects(fidx).contrast_bias
                        + axial_effects(0).contrast_bias)
    check("the design point's contrast bounded bias exceeds 0.0005",
          worst_con > BIAS_CONTRAST_MAX, repr(worst_con))
    check("the contrast bound is NOT the sum of two absolute bounds by default",
          "contrast_bias_from_absolute" not in
          _body(os.path.join("e1a_v5", "validation", "run.py")))


def test_d_bias_predicate_is_a_gate_not_a_wall() -> None:
    """A record whose certified set is small enough passes the predicate."""
    small = remainder_set_effects(RemainderSet(1.0e-5, "small set"), d=2)
    check("a small certified set fits inside the budget",
          plan.BIAS_PER_CELL + small.log_beta_bias <= BIAS_ABS_MAX)
    big = remainder_set_effects(RemainderSet(1.0e-2, "big set"), d=2)
    check("a large certified set does not",
          plan.BIAS_PER_CELL + big.log_beta_bias > BIAS_ABS_MAX)


# ===========================================================================
# BLOCKER E -- observation qualification
# ===========================================================================

def test_e_localisation_ratio_is_in_detector_coordinates() -> None:
    sig, p, r = nm.eye(2), nm.scale(nm.eye(2), 0.1), nm.scale(nm.eye(2), 0.01)
    check("S_y = P Sigma P^T",
          close(observed_signal_covariance(sig, p)[0][0], 0.01))
    got = localization_ratio(sig, r, p)
    check("the auditor's P = 0.1 I case gives exactly 1.0", close(got, 1.0),
          repr(got))
    check("and therefore FAILS the 0.05 ceiling",
          got > LOCALIZATION_RATIO_CEILING)
    check("the latent-only comparison V5 used would have PASSED",
          localization_ratio(sig, r, nm.eye(2)) <= LOCALIZATION_RATIO_CEILING)
    check("P is a required argument, not an optional one",
          _raises(lambda: localization_ratio(sig, r)))


def test_e_envelope_is_independent_of_branch_b() -> None:
    body = _body(os.path.join("e1a_v5", "validation", "harness.py"))
    start = body.index("def _analyse_record")
    region = body[start:body.index("def design_specs")]
    for forbidden in ("qualify_observation(fit", "fit.sigma_free, spec.r_obs, spec.p_matrix, fit.a_free"):
        check(f"the fitted model no longer qualifies the apparatus: {forbidden!r}",
              forbidden not in region)
    check("qualification goes through the independent envelope",
          "qualify_observation_envelope(envelope)" in region)
    obs_body = _body(os.path.join("e1a_v5", "observation.py"))
    check("the old fitted-model entry point is gone",
          "def qualify_observation(" not in obs_body)
    env_src = obs_body[obs_body.index("class ObservationEnvelope"):
                       obs_body.index("def qualify_observation_envelope")]
    for forbidden in ("fit", "free"):
        check(f"the envelope declares no Branch-B field containing {forbidden!r}",
              forbidden not in env_src)


def test_e_envelope_is_a_worst_case() -> None:
    spec, h = design_specs(n_frames=64)[0]
    env = observation_envelope(h, plan.T_REF, spec, axial_effects(0).rho)
    q = qualify_observation_envelope(env)
    check("the nominal design point is observation-qualified", q.valid,
          str([r.code for r in q.refusals]))
    check("the reported worst case exceeds the nominal value",
          q.localization_ratio_upper > q.localization_ratio
          and q.exposure_fraction_upper > q.exposure_fraction
          and q.bandwidth_product_upper > q.bandwidth_product)
    check("every worst case is inside its ceiling",
          q.localization_ratio_upper <= LOCALIZATION_RATIO_CEILING
          and q.exposure_fraction_upper <= 0.1
          and q.bandwidth_product_upper <= 0.2)
    check("the scale range comes from the plan, not from a fit",
          design_log_beta_range()[1] > 0.0 and design_log_beta_range()[0] < 0.0)
    wider = type(env)(**{**env.__dict__, "log_beta_range": (-1.0, 1.0)})
    check("a wider declared scale range gives a larger worst case",
          qualify_observation_envelope(wider).localization_ratio_upper
          > q.localization_ratio_upper)
    check("the exposure-averaged ratio keeps its own separate role",
          "exposure_averaged_ratio" in q.as_dict())


def test_e_noise_hi_fails_with_identity_and_nontrivial_p() -> None:
    kw = instantiate("CTL-NOISE-HI").spec_kwargs
    spec, h = design_specs(n_frames=64, **kw)[0]
    env = observation_envelope(h, plan.T_REF, spec, axial_effects(0).rho)
    q = qualify_observation_envelope(env)
    check("CTL-NOISE-HI fails with P = I", not q.valid)
    check("its ratio is far above the ceiling",
          q.localization_ratio > 4.0 * LOCALIZATION_RATIO_CEILING,
          repr(q.localization_ratio))
    scaled = nm.scale(nm.eye(2), 0.37)
    rotated = nm.matmul(scaled, nm.mat([[0.8, -0.6], [0.6, 0.8]]))
    env_p = type(env)(**{**env.__dict__, "p_matrix": rotated})
    q_p = qualify_observation_envelope(env_p)
    check("CTL-NOISE-HI fails with a nontrivial P too", not q_p.valid)
    check("a nontrivial P is not silently absorbed",
          not close(q_p.localization_ratio, q.localization_ratio, 1e-9))
    # A qualified world stays qualified through a nontrivial P, because the
    # ratio is invariant under an invertible P applied to BOTH sides.
    good_spec, good_h = design_specs(n_frames=64)[0]
    good = observation_envelope(good_h, plan.T_REF, good_spec,
                                axial_effects(0).rho)
    moved = type(good)(**{
        **good.__dict__, "p_matrix": rotated,
        "r_obs": nm.symmetrise(nm.matmul(nm.matmul(rotated, good.r_obs),
                                         nm.transpose(rotated))),
    })
    check("a consistent change of detector coordinates changes nothing",
          close(qualify_observation_envelope(moved).localization_ratio,
                qualify_observation_envelope(good).localization_ratio, 1e-9))


# ===========================================================================
# BLOCKER F -- the gate calibration receipt
# ===========================================================================

def _good_receipt(exp, **over) -> GateCalibrationReceipt:
    base = dict(
        family=GateFamily.CENTRE, procedure_version=exp.procedure_version,
        analysis_identity=exp.analysis_identity,
        validation_identity=exp.validation_identity,
        plan_identity=exp.plan_identity,
        seed_map_identity=exp.seed_map_identity,
        calibration_seed_namespace=exp.calibration_seed_namespace,
        calibration_identity="CAL-CENTRE-01/4000",
        domain_identity=exp.domain_identity, replicates=4000, radius=2.5e-3,
        coverage_target=exp.coverage_target, result_digest="b" * 64,
        released=True,
    )
    base.update(over)
    return GateCalibrationReceipt(**base).sealed()


def test_f_receipt_binds_every_identity() -> None:
    exp = gate_expectations()
    r = _good_receipt(exp)
    check("a genuine receipt verifies",
          GateLimit.from_receipt(0.0, r, GateFamily.CENTRE, exp).usable)
    check("the digest covers every bound field",
          GATE_DIGEST_MISMATCH in GateLimit.from_receipt(
              0.0, GateCalibrationReceipt(**{**r.__dict__, "replicates": 1}),
              GateFamily.CENTRE, exp).defects)
    check("the receipt binds the running analysis identity",
          r.analysis_identity == exp.analysis_identity and len(r.analysis_identity) == 64)
    check("the receipt binds the frozen plan identity",
          r.plan_identity == plan_identity())
    check("a plain string is not a receipt",
          GATE_NOT_A_RECEIPT in
          GateLimit.from_receipt(0.0, "any-identity", GateFamily.CENTRE, exp).defects)


def test_f_fixture_isolation_is_by_type() -> None:
    fx = synthetic_calibrated_gate_fixture(GateFamily.STATIONARITY, 1e-3)
    exp = gate_expectations()
    check("the fixture is its own type",
          isinstance(fx, SyntheticGateFixture)
          and not isinstance(fx, GateCalibrationReceipt))
    check("there is no forgeable fixture flag on the production class",
          "fixture_only" not in str(GateCalibrationReceipt.__dataclass_fields__))
    check("a fixture cannot reach the production builder",
          GATE_FIXTURE_IN_PRODUCTION in
          GateLimit.from_receipt(0.0, fx, GateFamily.STATIONARITY, exp).defects)
    check("a receipt cannot reach the fixture builder",
          not GateLimit.from_fixture(0.0, _good_receipt(exp),
                                     GateFamily.CENTRE).usable)
    body = _body(os.path.join("e1a_v5", "validation", "run.py"))
    check("the runner reaches fixtures only through the fixture constructor",
          "GateLimit.from_fixture(stat, fixtures[family], family)" in body)


def test_f_live_gate_state_is_uncalibrated() -> None:
    check("no production receipt exists", not NO_GATE_RECEIPTS)
    exp = gate_expectations()
    for fam in GateFamily:
        g = GateLimit.from_receipt(0.0, NO_GATE_RECEIPTS.get(fam), fam, exp)
        check(f"the {fam.value} gate is UNCALIBRATED", g.passes(1.0) is None)
    check("the live procedure version is 6", PROCEDURE_VERSION == 6)


# ===========================================================================
# BLOCKER G -- the two negative controls
# ===========================================================================

def test_g_eta_t_control_draws_fresh_auxiliary_measurements() -> None:
    stream = Stream(SeedMap().replicate_seed(ENGINEERING, "ETA-AUX", 0),
                    label="eng/eta")
    vector, phi, measured = auxiliary_measurement({}, stream)
    check("the generating law draws every declared primitive",
          len(phi) == len(vector.primitives))
    check("the draw is not the nominal point", any(v != 0.0 for v in phi))
    check("the shared thermometry latent is in the GENERATING law",
          plan.LATENT_THERMOMETRY in vector.latents)
    check("every record gets a measured field model", len(measured) == 8)
    k0 = measured[0][1]
    nominal = plan.thermal_hessian(schur_complement(plan.nominal_k3(0)), plan.T_REF)
    check("the measured locked field differs from the nominal one",
          nm.max_abs(nm.sub(k0.h_eff, nominal)) > 0.0)
    check("the measured observation calibration moves too",
          k0.dt != plan.timing(schur_complement(plan.nominal_k3(0)))[0]
          or k0.t_exp != plan.timing(schur_complement(plan.nominal_k3(0)))[1])
    # Empirical: the latent really does correlate the two standards.
    s = Stream(1234, label="eng/eta/corr")
    v = plan.primitive_vector()
    i = v.index_of(plan.PRIMITIVE_K_STANDARD)
    j = v.index_of(plan.PRIMITIVE_T_STANDARD)
    draws = [v.draw(s) for _ in range(4000)]
    mx = sum(d[i] for d in draws) / len(draws)
    my = sum(d[j] for d in draws) / len(draws)
    sxy = sum((d[i] - mx) * (d[j] - my) for d in draws) / (len(draws) - 1)
    sxx = sum((d[i] - mx) ** 2 for d in draws) / (len(draws) - 1)
    syy = sum((d[j] - my) ** 2 for d in draws) / (len(draws) - 1)
    emp = sxy / math.sqrt(sxx * syy)
    check("the drawn data carry the declared correlation",
          abs(emp - plan.ETA_T_CORRELATION) < 0.06, repr(emp))


def test_g_eta_t_control_asserts_no_direction() -> None:
    body = _body(os.path.join("e1a_v5", "validation", "run.py"))
    check("no executable code claims a direction",
          "understate" not in body and "overstate" not in body)
    correct = experiment_calibration()
    wrong = experiment_calibration(omit_eta_t_covariance=True)
    k = correct.keys[0]
    check("the two covariance models give different uncertainties",
          correct.absolute_sigma(k).point != wrong.absolute_sigma(k).point)
    case = CASES_BY_ID["CTL-ETA-T-COV"]
    check("the release event is false complete support",
          case.false_support_event
          and case.expected_event is ExpectedEvent.COMPLETE_SUPPORT)
    check("the acceptance rule is the T negative-control bound",
          "0.025" in case.acceptance_rule and "false complete support"
          in case.acceptance_rule)
    check("the plan requires 5000 replicates", case.replicates == 5000)


def test_g_axial_memory_qualification_is_derived() -> None:
    """No flag anywhere: the failure comes out of a measurement."""
    for path in (os.path.join("e1a_v5", "validation", "run.py"),
                 os.path.join("e1a_v5", "validation", "harness.py")):
        body = _body(path)
        check(f"{path} sets no temporal qualification flag",
              "temporal_reduction_qualified=False" not in body
              and "temporal_qualified=False" not in body
              and "temporal_qualified=True" not in body)
    ids = {r["case_id"] for r in deterministic_controls()}
    check("the hand-set refusal control is gone", "REF-AXIAL-REFUSAL" not in ids)
    check("a derived temporal reference replaces it",
          "REF-TEMPORAL-QUALIFICATION" in ids)

    nominal_spec, nominal_h = design_specs(n_frames=16)[0]
    a, sigma = true_system(nominal_spec)
    q = temporal_qualification(
        a, sigma, nm.scale(nominal_spec.h_true, K_B * plan.T_REF),
        nominal_spec.p_matrix, nominal_spec.r_obs, nominal_spec.b_det,
        Stream(11, label="eng/temporal/nom"))
    check("a 2D world is QUALIFIED by the measurement",
          q["status"] == TEMPORAL_QUALIFIED, str(q))
    mem = axial_memory_specs(n_frames=16)[0][0]
    a3, s3 = axial_memory_dynamics(mem)
    qm = temporal_qualification(
        a3, s3, schur_complement(mem.k3), mem.p_matrix, mem.r_obs, mem.b_det,
        Stream(12, label="eng/temporal/mem"))
    check("a hidden-memory world is UNQUALIFIED by the same machinery",
          qm["status"] == TEMPORAL_UNQUALIFIED, str(qm))
    check("the violation is well outside the measurement band",
          qm["semigroup_residual"] > 2.0 * qm["band"])
    check("a band too wide to exclude anything is UNRESOLVED, not qualified",
          plan.RESPONSE_RESOLUTION > 0.0
          and q["band"] <= plan.RESPONSE_RESOLUTION)


def test_g_axial_memory_world_and_classification() -> None:
    mem = axial_memory_specs(n_frames=16)[0][0]
    a3, s3 = axial_memory_dynamics(mem)
    check("the generator really is three-dimensional", len(a3) == 3)
    check("the lateral marginal is exactly the Schur density",
          nm.max_abs(nm.sub(
              [[s3[i][j] for j in range(2)] for i in range(2)],
              nm.scale(nm.spd_inverse(schur_complement(mem.k3)),
                       K_B * mem.temperature))) < 1e-30)
    check("the construction-time residual separates the two worlds",
          exact_semigroup_residual(a3, s3) > 0.1)
    case = CASES_BY_ID["CTL-AXIAL-MEMORY"]
    check("the expected physical classification is recorded in the plan",
          "TEMPORAL_MODEL_UNQUALIFIED" in case.expectation)
    check("the release event is separately counted false support",
          case.false_support_event and case.replicates == 5000)
    check("the B side gets no hidden coordinate",
          len(mem.p_matrix) == 2 and len(mem.p_matrix[0]) == 2)


def test_g_design_evidence_is_derived() -> None:
    ev = design_evidence(plan.nominal_k3(0), plan.T_REF)
    check("a constructed 2D world derives a qualified temporal item",
          ev.temporal_reduction_qualified is True)
    check("the derivation is a computation on the built world",
          plan.construction_temporal_qualified(
              schur_complement(plan.nominal_k3(0)), plan.T_REF) is True)
    body = _body(os.path.join("e1a_v5", "reduction.py"))
    check("the evidence constructor takes the temporal item as a parameter",
          "temporal_qualified: bool = True" in body)


def test_g_response_measurement_is_honest() -> None:
    """The measurement reports its own error and does not fit anything."""
    spec, h = design_specs(n_frames=16)[0]
    a, sigma = true_system(spec)
    rs = ResponseSpec(a_drift=a, sigma=sigma, p_matrix=spec.p_matrix,
                      r_obs=spec.r_obs, b_det=spec.b_det,
                      tau=plan.RESPONSE_LAG_FRACTION * plan.drag_coefficient()
                      / min(nm.eigh(schur_complement(plan.nominal_k3(0)))[0]),
                      trials=400, displacement_sd=plan.RESPONSE_DISPLACEMENT_SD)
    out = generate_response_record(rs, Stream(21, label="eng/resp"))
    check("the measurement reports its own standard error",
          out["residual_standard_error"] > 0.0)
    check("more trials shrink the standard error",
          generate_response_record(
              type(rs)(**{**rs.__dict__, "trials": 1600}),
              Stream(22, label="eng/resp"))["residual_standard_error"]
          < out["residual_standard_error"])
    check("a measurement with too few trials refuses",
          _raises(lambda: generate_response_record(
              type(rs)(**{**rs.__dict__, "trials": 1}),
              Stream(23, label="eng/resp"))))
    body = _body(os.path.join("e1a_v5", "generate.py"))
    start = body.index("def generate_response_record")
    region = body[start:body.index("def exact_semigroup_residual")]
    check("the response measurement fits nothing",
          "minimise" not in region and "fit_record" not in region)


# ===========================================================================
# Plan contract, seeds, identities
# ===========================================================================

def test_plan_contract_covers_the_required_fields() -> None:
    for field in ("case_id", "purpose", "family", "replicates", "seed_namespace",
                  "expected_event", "expectation", "false_support_event",
                  "acceptance_rule", "detail"):
        check(f"the contract compares {field!r}", field in COMPARED_FIELDS)
    report = check_correspondence(ALL_CASES)
    check("every case matches the machine plan", report.ok,
          "; ".join(report.as_list()[:4]))
    doc = load_plan()
    for field, value in (("acceptance_rule", "something else"),
                         ("expectation", "something else"),
                         ("false_support_event", False),
                         ("replicates", 7)):
        mutated = {**doc, "cases": [
            ({**c, field: value} if c["case_id"] == "CTL-NOISE-HI" else c)
            for c in doc["cases"]]}
        check(f"a plan/code difference in {field!r} fails",
              not check_correspondence(ALL_CASES, mutated).ok)
        check(f"require_correspondence raises on {field!r}",
              _raises(lambda m=mutated: require_correspondence(ALL_CASES, m)))
    check("there is no warning-only mode",
          "warn" not in _body(os.path.join("e1a_v5", "validation", "contract.py")))
    check("the plan has a byte identity", len(plan_identity()) == 64)


def test_plan_counts_and_release_events() -> None:
    doc = load_plan()
    rel = doc["negative_control_release"]
    for cid in ("CTL-ETA-T-COV", "CTL-AXIAL-MEMORY"):
        check(f"{cid} names FALSE_SUPPORT as its primary event",
              rel[cid]["primary_release_event"] == "FALSE_SUPPORT")
        check(f"{cid} requires 5000 replicates", rel[cid]["replicates"] == 5000)
        check(f"{cid} carries the 0.025 CP rule",
              "0.025" in rel[cid]["acceptance_rule"])
        check(f"{cid} is 5000 in the case block",
              CASES_BY_ID[cid].replicates == 5000)
    check("the covariance consequence stays mandatory output",
          "NOT a substitute" in rel["CTL-ETA-T-COV"]["secondary_status"])
    check("the axial-memory expected classification is stated",
          "TEMPORAL_MODEL_UNQUALIFIED"
          in rel["CTL-AXIAL-MEMORY"]["expected_physical_classification"])
    check("the case inventory is unchanged at 51", len(ALL_CASES) == 51)


def test_v6_seeds_are_frozen_and_disjoint() -> None:
    sm = SeedMap()
    check("the V6 root is new",
          ROOT.endswith("v6/2026-10-06")
          and ROOT not in (ROOT_V5, ROOT_V4, ROOT_V3, ROOT_V2))
    check("five confirmatory families, all versioned v6",
          len(CONFIRMATORY_FAMILIES) == 5
          and all(f.endswith("-v6") for f in CONFIRMATORY_FAMILIES))
    check("the engineering namespace is v6 and separate",
          ENGINEERING == "engineering-v6" and ENGINEERING not in CONFIRMATORY_FAMILIES)
    for i, fam in enumerate(CONFIRMATORY_FAMILIES):
        for root, old, label in ((ROOT_V5, FAMILIES_V5[i], "V5"),
                                 (ROOT_V4, FAMILIES_V4[i], "V4"),
                                 (ROOT_V3, FAMILIES_V3[i], "V3"),
                                 (ROOT_V2, FAMILIES_V2[i], "V2")):
            check(f"{fam} is disjoint from its {label} stream",
                  sm.disjoint_from(fam, root, old, "CTL-AXIAL-MEMORY", 128))
        check(f"{fam} is disjoint from EVERY engineering stream",
              sm.disjoint_from_all_engineering(fam, "CTL-AXIAL-MEMORY", 256))
    check("engineering shares no seed with any confirmatory family",
          sm.engineering_disjoint_from_confirmatory("CTL-AXIAL-MEMORY", 256))
    for eng, root in ((ENGINEERING_V5, ROOT_V5), (ENGINEERING_V4, ROOT_V4)):
        check(f"the superseded engineering stream {eng} is retained for checking",
              isinstance(eng, str) and isinstance(root, str))


def test_v6_identity_binds_every_result_affecting_module() -> None:
    from e1a_v5.identity import VALIDATION_MODULES, compute_identities
    for mod in ("certified.py", "calibration.py", "observation.py",
                "reduction.py", "generate.py",
                os.path.join("validation", "contract.py"),
                os.path.join("validation", "harness.py"),
                os.path.join("validation", "run.py")):
        check(f"the validation identity binds {mod}", mod in VALIDATION_MODULES)
    ids = compute_identities(plan.IDENTITY_CONFIGURATION)
    check("six distinct 64-hex identities",
          len({*ids.as_dict().values()}) == 6
          and all(len(v) == 64 for v in ids.as_dict().values()))
    check("the declared configuration is procedure version 6",
          plan.IDENTITY_CONFIGURATION["procedure_version"] == 6)
    check("the domain identity matches the runner's",
          plan.IDENTITY_CONFIGURATION["domain_identity"] == DOMAIN_IDENTITY)


def test_deterministic_battery_passes() -> None:
    for r in deterministic_controls():
        check(f"deterministic control {r['case_id']} passes", r["passed"],
              str(r.get("observed"))[:200])


def main() -> int:
    print("E1a V-STAGE PROCEDURE VERSION 6 -- CORE REPAIR REGRESSIONS")
    print("=" * 70)
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            print(f"\n{name[5:].replace('_', ' ')}")
            fn()
    print("=" * 70)
    print(f"RESULT: {PASSED} passed, {FAILED} failed")
    print("\nSCIENTIFIC ACCOUNTING")
    print("  REAL EXPERIMENT DATA ....... 0")
    print("  CONFIRMATORY SEEDS USED .... 0")
    print("  CALIBRATION EXECUTIONS ..... 0")
    print("  OFFICIAL CAMPAIGN JOBS ..... 0")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
