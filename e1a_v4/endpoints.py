"""The four adopted endpoints. Every constant is read from the contract.

P1  two-block geometry gate, union-valid, no independence asserted
P2  cross-field commensurability, intersection-union equivalence, no Bonferroni
P3  absolute benchmark, EVERY tested field, conjunctive, fail-closed
P4  DETERMINISTIC PHYSICAL/THEORETICAL CONSISTENCY CHECK, no Branch-B data

CLASSIFICATION
    P2 / P3 acceptance rules .... EXACT (the adopted inequalities)
    their uncertainty inputs .... APPROXIMATION (first-order propagation)
    P1 block-1 p-values ......... REQUIRES STOCHASTIC VALIDATION
    P4 ......................... EXACT UNDER STATED ASSUMPTIONS
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Mapping, Sequence

from . import K_B
from .calibration import BLOCK1_GATES, CalibrationArtifact, block2_p_value, require_calibration
from .contract import ContractBinding
from .geometry import FieldAnalysis
from .numerics import Refusal
from .status import AnalysisStatus


@dataclass(frozen=True)
class UncertaintyModel:
    """HYPOTHETICAL INSTRUMENT SCENARIO. Not a measured apparatus capability."""

    sigma_cm: float
    sigma_fs: float
    sigma_stat: Mapping[str, float]
    label: str = "HYPOTHETICAL INSTRUMENT SCENARIO"

    @classmethod
    def from_contract(cls, binding: ContractBinding, sigma_stat: Mapping[str, float]) -> "UncertaintyModel":
        sc = binding.data["hypothetical_uncertainty_scenario"]
        return cls(sigma_cm=float(sc["sigma_cm"]), sigma_fs=float(sc["sigma_fs_derived"]),
                   sigma_stat=dict(sigma_stat), label=str(sc["label"]))


@dataclass(frozen=True)
class EndpointResult:
    name: str
    passed: bool
    detail: str
    rows: tuple[tuple, ...] = ()


# ------------------------------------------------------------------------ P1
def p1_geometry(
    analysis: FieldAnalysis,
    binding: ContractBinding,
    *,
    procedure_identity: str,
    H_A: Sequence[Sequence[float]],
    n: int,
    phi_modes: Sequence[float],
    artifact: CalibrationArtifact | None,
) -> EndpointResult:
    """Two-block union-valid gate.

    reject iff  p_min(G1..G4) < alpha_1   OR   p(G5) < alpha_2

    The union bound is valid under ARBITRARY dependence between the blocks. No
    independence is asserted, and none is needed.

    *** STOCHASTIC NULL CALIBRATION NOT RUN: without a matching artifact this
    refuses rather than assuming a threshold. ***
    """
    if not analysis.is_estimated and analysis.status not in (AnalysisStatus.GEOMETRY_FAIL,):
        return EndpointResult("P1", False, f"fail-closed on status {analysis.status.value}")
    art = require_calibration(artifact, procedure_identity=procedure_identity,
                              H_A=H_A, n=n, field_id=analysis.field_id)
    observed = {"G1": analysis.g1, "G2": analysis.g2_spread,
                "G3": max(analysis.g3) if analysis.g3 else None, "G4": analysis.g4}
    if any(v is None for v in observed.values()) or analysis.g5 is None:
        raise Refusal("P1 requires all five gate statistics")
    p_gates = {g: art.p_value(g, float(observed[g])) for g in BLOCK1_GATES}
    p_min = min(p_gates.values())
    critical = art.critical_p_min()
    block1_reject = p_min < critical
    p5 = block2_p_value(float(analysis.g5), float(phi_modes[0]), n)
    block2_reject = p5 < binding.alpha_2
    passed = not (block1_reject or block2_reject)
    rows = tuple((g, float(observed[g]), p_gates[g]) for g in BLOCK1_GATES) + \
           (("G5", float(analysis.g5), p5),)
    return EndpointResult(
        "P1", passed,
        f"p_min={p_min:.4g} vs critical={critical:.4g} (alpha_1={binding.alpha_1}); "
        f"p(G5)={p5:.4g} vs alpha_2={binding.alpha_2}; union bound, no independence asserted",
        rows)


# ------------------------------------------------------------------------ P2
def p2_cross_field(
    analyses: Mapping[str, FieldAnalysis],
    binding: ContractBinding,
    unc: UncertaintyModel,
) -> EndpointResult:
    """Intersection-union equivalence of beta ratios against the reference field.

    Acceptance requires the FULL interval inside [1-delta, 1+delta]. This is not
    'the CI contains 1' and not 'p > 0.05'; those answer different questions.
    """
    ref_id = binding.reference_field_id
    if ref_id not in analyses:
        return EndpointResult("P2", False, f"reference field {ref_id} absent")
    if not analyses[ref_id].is_estimated:
        return EndpointResult("P2", False,
                              f"reference beta not estimated ({analyses[ref_id].status.value})")
    beta_ref = analyses[ref_id].require_beta()
    delta, z = binding.delta_cross, binding.z_cross
    rows, passed = [], True
    for spec in binding.fields:
        fid = spec["id"]
        if fid == ref_id:
            continue
        a = analyses.get(fid)
        if a is None or not a.is_estimated:
            rows.append((fid, None, None, None, False))
            passed = False
            continue
        r = a.require_beta() / beta_ref
        h = z * math.sqrt(2 * unc.sigma_fs ** 2
                          + unc.sigma_stat[fid] ** 2 + unc.sigma_stat[ref_id] ** 2)
        lo, hi = r * (1 - h), r * (1 + h)
        inside = lo >= 1 - delta and hi <= 1 + delta
        passed = passed and inside
        rows.append((fid, r, lo, hi, inside))
    return EndpointResult("P2", passed,
                          f"delta_cross={delta}, z={z}, {len(rows)} comparisons, "
                          "intersection-union, no Bonferroni", tuple(rows))


# ------------------------------------------------------------------------ P3
def p3_absolute(
    analyses: Mapping[str, FieldAnalysis],
    binding: ContractBinding,
    unc: UncertaintyModel,
) -> EndpointResult:
    """Absolute equivalence around beta = 1 at EVERY tested field, conjunctive.

    One failed field fails P3. One non-ESTIMATED field fails P3. Reference-only
    success is insufficient.
    """
    delta, z = binding.delta_abs, binding.z_abs
    rows, passed = [], True
    for spec in binding.fields:
        fid = spec["id"]
        a = analyses.get(fid)
        if a is None or not a.is_estimated:
            rows.append((fid, None, None, None, False))
            passed = False
            continue
        b = a.require_beta()
        h = z * math.sqrt(unc.sigma_cm ** 2 + unc.sigma_fs ** 2 + unc.sigma_stat[fid] ** 2)
        lo, hi = b * (1 - h), b * (1 + h)
        inside = lo >= 1 - delta and hi <= 1 + delta
        passed = passed and inside
        rows.append((fid, b, lo, hi, inside))
    return EndpointResult("P3", passed,
                          f"delta_abs={delta}, z={z}, all {len(rows)} fields required",
                          tuple(rows))


# ------------------------------------------------------------------------ P4
def declared_entropy_relation(E: float, T: float) -> dict[str, float]:
    """The adopted relation. Consumes NO Branch-B data."""
    q = E * K_B * T                 # heat delivered to the reservoir, no-work transition
    ds_med = q / T                  # = +k_B E
    ds_sys = -K_B * E
    return {"heat_J": q, "ds_med": ds_med, "ds_sys": ds_sys, "ds_tot": ds_med + ds_sys}


def p4_consistency(
    binding: ContractBinding,
    temperatures: Sequence[float] = (298.0, 318.0),
    E: float = 5.0,
    relation=declared_entropy_relation,
    tol: float = 1e-12,
) -> EndpointResult:
    """DETERMINISTIC PHYSICAL/THEORETICAL CONSISTENCY CHECK.

    Verifies, on declared constants only:
        ds_med = +k_B E   identical across temperatures though the heat differs
        ds_sys = -k_B E
        ds_tot = 0
    The constrained-macrostate statement stays SEPARATE and symbolic:
        Delta S_constr = k_B E + O(U^2 / (T^2 C_V))
    `Delta S_total = k_B E` is not reintroduced anywhere.

    Passing is NOT experimental confirmation of entropy production.
    """
    sem = binding.data["entropy_semantics"]
    if "NOT total stochastic entropy production" not in sem["prohibited"]:
        return EndpointResult("P4", False, "contract lost the total-entropy prohibition")
    rows, passed = [], True
    for T in temperatures:
        r = relation(E, T)
        med_ok = abs(r["ds_med"] / K_B - E) <= tol
        sys_ok = abs(r["ds_sys"] / K_B + E) <= tol
        tot_ok = abs(r["ds_tot"]) <= tol * K_B
        ok = med_ok and sys_ok and tot_ok
        passed = passed and ok
        rows.append((T, r["heat_J"], r["ds_med"] / K_B, r["ds_sys"] / K_B, r["ds_tot"], ok))
    meds = [row[2] for row in rows]
    identical = max(meds) - min(meds) <= tol if meds else False
    passed = passed and identical
    return EndpointResult("P4", passed,
                          "deterministic consistency check on declared constants; "
                          "ds_med identical across T: " + str(identical) +
                          "; NOT experimental evidence", tuple(rows))
