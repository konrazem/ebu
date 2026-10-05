"""E1a v5 candidate: numerical kernel, units, packets and Branch-A validation.

**EXECUTION CLASS: NON-MODEL-ADVANCING STATIC/PURE.** Closed-form algebra,
exact rational/analytic references and structured-refusal checks only. No
scientific RNG, no trajectory, no calibration execution, no campaign job.
"""

from __future__ import annotations

import math

from e1a_v5 import numerics as nm
from e1a_v5 import units as un
from e1a_v5.branch_a import (
    normalised_hessian,
    relaxation_times,
    resistance_tensor,
    stokes_drag,
    validate_branch_a_primitives,
    validate_primitives,
)
from e1a_v5.numerics import NumericalFailure
from e1a_v5.packets import RECORDS, CONTRASTS, BranchAPacket, ValueKind
from e1a_v5.refusals import (
    ALL_CODES,
    NUMERICAL_REPRESENTATION_FAILURE,
    PRIMITIVE_PHYSICALLY_INVALID,
    THERMOMETRY_UNQUALIFIED,
    Refusal,
)

PASSED = 0
FAILED = 0


def check(label: str, cond: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
    else:
        FAILED += 1
        print(f"  [FAIL] {label} {detail}")


def close(a: float, b: float, tol: float = 1e-12) -> bool:
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


# --------------------------------------------------------------------------
def test_units_fail_closed() -> None:
    check("um -> m", close(un.to_si(1.0, "um", un.LENGTH), 1e-6))
    check("mPa.s -> Pa.s", close(un.to_si(0.89, "mPa.s", un.VISCOSITY), 0.89e-3))
    check("uN/m -> N/m", close(un.to_si(100.0, "uN/m", un.STIFFNESS), 1e-4))
    check("pN/um -> N/m", close(un.to_si(1.0, "pN/um", un.STIFFNESS), 1e-6))
    for value, unit, dim, why in [
        (1.0, "um", un.VISCOSITY, "length offered as viscosity"),
        (1.0, "mPa.s", un.LENGTH, "viscosity offered as length"),
        (1.0, "uN/m", un.FORCE, "stiffness offered as force"),
        (1.0, "micron", un.LENGTH, "unknown unit string"),
        (float("nan"), "m", un.LENGTH, "non-finite value"),
        (float("inf"), "m", un.LENGTH, "infinite value"),
        (1.0, None, un.LENGTH, "absent unit"),
    ]:
        try:
            un.to_si(value, unit, dim)
            check(f"closed: {why}", False, "conversion succeeded")
        except un.UnitError:
            check(f"closed: {why}", True)
    check("k_B exact", un.K_B == 1.380649e-23)
    check("thermal energy", close(un.thermal_energy(298.0), 1.380649e-23 * 298.0))
    for bad in (0.0, -1.0, float("nan")):
        try:
            un.thermal_energy(bad)
            check(f"closed: T={bad}", False)
        except un.UnitError:
            check(f"closed: T={bad}", True)


def test_linear_algebra_references() -> None:
    A = nm.mat([[2, 1], [1, 3]])
    check("spd inverse", nm.max_abs(nm.sub(nm.spd_inverse(A), nm.mat([[0.6, -0.2], [-0.2, 0.4]]))) < 1e-15)
    check("logdet", close(nm.spd_logdet(A), math.log(5.0)))
    vals, Q = nm.eigh(A)
    check("eig backward error", nm.eig_backward_error(A, vals, Q) < nm.BACKWARD_ERROR_CEILING)
    check("eig ascending", vals[0] <= vals[1])
    check("cond2", close(nm.cond2_spd(A), vals[1] / vals[0]))
    # matrix functions: sqrtm^2 = A, logm then expm returns A
    S = nm.sqrtm_spd(A)
    check("sqrtm squared", nm.max_abs(nm.sub(nm.matmul(S, S), A)) < 1e-13)
    check("inv sqrtm", nm.max_abs(nm.sub(nm.matmul(nm.inv_sqrtm_spd(A), S), nm.eye(2))) < 1e-13)
    check("expm(logm)", nm.max_abs(nm.sub(nm.expm(nm.logm_spd(A)), A)) < 1e-12)
    # repeated eigenvalues are valid; near-zero is refused
    check("repeated eigenvalues allowed", nm.max_abs(nm.sub(nm.sqrtm_spd(nm.scale(nm.eye(2), 4.0)), nm.scale(nm.eye(2), 2.0))) < 1e-14)
    try:
        nm.logm_spd(nm.mat([[1.0, 0.0], [0.0, 1e-20]]))
        check("near-zero eigenvalue refused", False)
    except NumericalFailure:
        check("near-zero eigenvalue refused", True)
    try:
        nm.cholesky(nm.mat([[1.0, 2.0], [2.0, 1.0]]))
        check("indefinite refused", False)
    except NumericalFailure:
        check("indefinite refused", True)
    # generalized eigenvalues via symmetric whitening
    lam = nm.generalized_eigvals_spd(nm.scale(nm.eye(2), 2.1), nm.eye(2))
    check("generalized eigenvalues", all(close(v, 2.1) for v in lam))
    # expm against the analytic rotation-decay reference
    w = 0.7
    E = nm.expm(nm.mat([[-1.0, -w], [w, -1.0]]))
    e = math.exp(-1.0)
    ref = nm.mat([[e * math.cos(w), -e * math.sin(w)], [e * math.sin(w), e * math.cos(w)]])
    check("expm analytic", nm.max_abs(nm.sub(E, ref)) < 1e-14)
    # discrete Lyapunov
    P = nm.solve_lyapunov_discrete(nm.scale(nm.eye(2), 0.5), nm.eye(2))
    check("discrete Lyapunov", close(P[0][0], 1.0 / 0.75))


def test_normal_and_binomial() -> None:
    check("Phi(0)", close(nm.norm_cdf(0.0), 0.5))
    check("Phi inverse roundtrip", all(
        close(nm.norm_cdf(nm.norm_ppf(p)), p, 1e-13)
        for p in (1e-8, 0.001, 0.025, 0.5, 0.9, 0.975, 0.98, 1 - 1e-9)
    ))
    check("Phi^-1(0.975)", close(nm.norm_ppf(0.975), 1.959963984540054, 1e-12))
    check("Phi^-1(0.98)", close(nm.norm_ppf(0.98), 2.0537489106318225, 1e-12))
    # incomplete beta against closed forms
    check("I_x(1,1) = x", close(nm.betainc_reg(1.0, 1.0, 0.37), 0.37))
    check("I_x(2,1) = x^2", close(nm.betainc_reg(2.0, 1.0, 0.4), 0.16))
    check("I_x(1,2) = 1-(1-x)^2", close(nm.betainc_reg(1.0, 2.0, 0.4), 1 - 0.36))
    check("betaincinv roundtrip", close(nm.betainc_reg(3.0, 5.0, nm.betaincinv_reg(3.0, 5.0, 0.3)), 0.3, 1e-10))
    # Clopper-Pearson against known boundary behaviour
    check("CP upper k=0", nm.clopper_pearson_upper(0, 100) > 0.0)
    check("CP upper k=n is 1", nm.clopper_pearson_upper(10, 10) == 1.0)
    check("CP lower k=0 is 0", nm.clopper_pearson_lower(0, 10) == 0.0)
    check("CP monotone in k", nm.clopper_pearson_upper(5, 100) < nm.clopper_pearson_upper(20, 100))
    # exact binomial identity: CP upper u solves P(X <= k | u) = 1 - conf
    k, n, conf = 7, 200, 0.95
    u = nm.clopper_pearson_upper(k, n, conf)
    check("CP upper solves the binomial tail", close(nm.binom_cdf(k, n, u), 1 - conf, 1e-9))
    l = nm.clopper_pearson_lower(k, n, conf)
    check("CP lower solves the binomial tail", close(nm.binom_sf(k - 1, n, l), 1 - conf, 1e-9))
    # acceptance counts used by the release criteria
    kmax = nm.max_successes_for_upper_bound(5000, 0.025)
    check("size acceptance count", kmax == 106 and nm.clopper_pearson_upper(106, 5000) <= 0.025
          and nm.clopper_pearson_upper(107, 5000) > 0.025, f"got {kmax}")
    kmin = nm.min_successes_for_lower_bound(2000, 0.90)
    check("power acceptance count", kmin == 1823 and nm.clopper_pearson_lower(1823, 2000) >= 0.90
          and nm.clopper_pearson_lower(1822, 2000) < 0.90, f"got {kmin}")
    kdiag = nm.max_successes_for_upper_bound(5000, 0.005)
    check("diagnostic acceptance count", nm.clopper_pearson_upper(kdiag, 5000) <= 0.005
          and nm.clopper_pearson_upper(kdiag + 1, 5000) > 0.005, f"got {kdiag}")


def test_positive_primitives_old_f2() -> None:
    tiny = 5e-324
    ok, ref = validate_primitives(0.89e-3, 1e-6, 298.0)
    check("nominal primitives pass", not ref)
    # each primitive is judged separately; a positive product rescues nothing
    _, ref = validate_primitives(-0.89e-3, -1e-6, 298.0)
    codes = {r.predicate for r in ref}
    check("both negative primitives refused separately",
          "eta > 0" in codes and "a > 0" in codes, str(codes))
    check("product would have been positive", (-0.89e-3) * (-1e-6) > 0)
    for label, args, pred in [
        ("eta NaN", (float("nan"), 1e-6, 298.0), "eta not NaN"),
        ("eta inf", (float("inf"), 1e-6, 298.0), "eta finite"),
        ("eta zero", (0.0, 1e-6, 298.0), "eta > 0"),
        ("a zero", (0.89e-3, 0.0, 298.0), "a > 0"),
        ("T zero", (0.89e-3, 1e-6, 0.0), "T > 0"),
        ("T negative", (0.89e-3, 1e-6, -298.0), "T > 0"),
        ("eta subnormal", (tiny, 1e-6, 298.0), "1e-05 <= eta <= 1.0"),
        ("a subnormal", (0.89e-3, tiny, 298.0), "1e-08 <= a <= 0.0001"),
        ("eta absent", (None, 1e-6, 298.0), "eta present"),
        ("eta string", ("0.00089", 1e-6, 298.0), "eta numeric"),
        ("eta bool", (True, 1e-6, 298.0), "eta numeric"),
    ]:
        _, ref = validate_primitives(*args)
        check(f"refused: {label}", any(r.predicate == pred for r in ref),
              f"got {[r.predicate for r in ref]}")
    # the thermometry failure carries its own reason family
    _, ref = validate_primitives(0.89e-3, 1e-6, 0.0)
    check("T failure is thermometry", ref[0].code == THERMOMETRY_UNQUALIFIED)


def test_derived_quantities_defend_against_overflow() -> None:
    g, ref = stokes_drag(0.89e-3, 1e-6)
    check("stokes drag", close(g, 6 * math.pi * 0.89e-3 * 1e-6) and not ref)
    # product underflow is a numerical representation failure, never a clip
    g, ref = stokes_drag(5e-324, 5e-324)
    check("eta*a underflow refused",
          bool(ref) and ref[0].code == NUMERICAL_REPRESENTATION_FAILURE
          and ref[0].predicate == "eta * a != 0")
    check("underflow returns no value", math.isnan(g))
    _, ref = stokes_drag(0.89e-3, 1e-6, wall_correction=float("inf"))
    check("non-finite wall correction refused", bool(ref))
    _, ref = resistance_tensor(1.0, [1.0, 1.0, -1.0])
    check("negative anisotropy refused", bool(ref))
    _, ref = resistance_tensor(1.0, [1.0, 1.0])
    check("wrong anisotropy length refused", bool(ref))
    # H overflow
    _, ref = normalised_hessian(nm.mat([[1e300, 0], [0, 1e300]]), 1e-10)
    check("H overflow refused", bool(ref) and ref[0].code == NUMERICAL_REPRESENTATION_FAILURE)
    # H conditioning
    _, ref = normalised_hessian(nm.mat([[1e-4, 0], [0, 1e-7]]), 298.0)
    check("H conditioning refused", bool(ref) and ref[0].predicate == "cond2(H) <= 100.0")
    h, ref = normalised_hessian(nm.mat([[1e-4, 0], [0, 1e-4]]), 298.0)
    check("H nominal accepted", not ref and close(nm.cond2_spd(h), 1.0))
    # tau domain
    _, ref = relaxation_times(nm.scale(nm.eye(3), 1.0), nm.scale(nm.eye(3), 1e-30))
    check("tau outside domain refused", bool(ref))
    # full chain
    K = nm.mat([[1e-4, 0, 0], [0, 1e-4, 0], [0, 0, 2e-5]])
    d, ref = validate_branch_a_primitives(0.89e-3, 1e-6, 298.0, K)
    check("full chain nominal", not ref and d is not None and len(d.tau) == 3)
    d, ref = validate_branch_a_primitives(-0.89e-3, -1e-6, 298.0, K)
    check("full chain refuses before deriving", d is None and len(ref) == 2)


def test_packets_are_synthetic_only() -> None:
    check("eight records", len(RECORDS) == 8 and len(set(RECORDS)) == 8)
    check("six contrasts", len(CONTRASTS) == 6 and all(f.value != "theta0" for _, f in CONTRASTS))
    check("value kinds distinct", len({k.value for k in ValueKind}) == 6)
    check("synthetic kind is marked", ValueKind.SYNTHETIC_MEASURED.value == "SYNTHETIC_MEASURED_LIKE")
    try:
        BranchAPacket(
            block=RECORDS[0][0], field=RECORDS[0][1], k3=nm.eye(3),
            temperature=None, viscosity=None, bead_radius=None,
            centre=[0.0, 0.0], c_phi=nm.eye(2), phi_names=["a", "b"], synthetic=False,
        )
        check("non-synthetic packet refused", False)
    except ValueError:
        check("non-synthetic packet refused", True)


def test_refusal_codes_are_closed() -> None:
    check("codes closed", len(ALL_CODES) == 24)
    try:
        Refusal(code="NOT_A_CODE", predicate="x")
        check("unknown code refused", False)
    except ValueError:
        check("unknown code refused", True)
    r = Refusal(code=PRIMITIVE_PHYSICALLY_INVALID, predicate="eta > 0", reason="r")
    check("family mapping", r.family == "INVALID")
    check("refusal serialises", set(r.as_dict()) == {"code", "predicate", "reason", "family", "detail"})


def main() -> int:
    print("units fail closed")
    test_units_fail_closed()
    print("\nlinear algebra against analytic references")
    test_linear_algebra_references()
    print("\nnormal and binomial primitives")
    test_normal_and_binomial()
    print("\npositive primitives (old F2 rule)")
    test_positive_primitives_old_f2()
    print("\nderived quantity overflow defence")
    test_derived_quantities_defend_against_overflow()
    print("\npacket schema")
    test_packets_are_synthetic_only()
    print("\nrefusal codes")
    test_refusal_codes_are_closed()
    print(f"\nRESULT: {PASSED} passed, {FAILED} failed")
    print("Execution class: NON-MODEL-ADVANCING STATIC/PURE")
    print("  SCIENTIFIC RNG DRAWS ... 0")
    print("  OU TRAJECTORIES ........ 0")
    print("  CALIBRATION EXECUTIONS . 0")
    print("  OFFICIAL CAMPAIGN JOBS . 0")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
