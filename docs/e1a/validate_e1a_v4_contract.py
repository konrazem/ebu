"""E1a v4 - deterministic conformance validation of the adopted design authority.

DETERMINISTIC ONLY: parsing, hashing, string and numeric comparison. No RNG, no
trajectories, no model stepping, no simulation runner. Run from the repository root:

    python3 docs/e1a/validate_e1a_v4_contract.py
"""
import json, hashlib, os, re, sys

FD  = "docs/physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md"
BL  = "docs/theory/EBU_THEORY_BASELINE.md"
BLM = "docs/theory/EBU_THEORY_BASELINE.meta.json"
DS  = "docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md"
CT  = "docs/e1a/e1a_v4_design_contract.json"
FOUNDATION_FROZEN = "6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507"

def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()

fails, checks = [], 0
def chk(name, ok, detail=""):
    global checks
    checks += 1
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  -- {detail}" if detail else ""))
    if not ok: fails.append(name)

md = open(DS, encoding="utf-8").read()
c  = json.load(open(CT))
bl = open(BL, encoding="utf-8").read()
blm= json.load(open(BLM))

print("1. FROZEN FOUNDATION UNCHANGED")
chk("foundation sha256 equals the frozen value", sha(FD) == FOUNDATION_FROZEN, sha(FD))

print("\n2. CONTRACT HASH BINDINGS RESOLVE")
b = c["authority"]["binds"]
chk("contract -> foundation hash matches file", b["frozen_foundation"]["sha256"] == sha(FD))
chk("contract -> baseline hash matches file",   b["working_baseline"]["sha256"] == sha(BL))
chk("contract -> design hash matches file",     b["design_document"]["sha256"] == sha(DS))
chk("contract -> design byte count matches",    b["design_document"]["byte_count"] == os.path.getsize(DS))
chk("baseline meta sha256 matches baseline",    blm["sha256"] == sha(BL))
chk("baseline meta byte_count matches",         blm["byte_count"] == os.path.getsize(BL))
chk("baseline meta records the v4 design hash", blm["e1a_v4_design"]["design_sha256"] == sha(DS))

print("\n3. EVERY ADOPTED NUMERICAL CONSTANT PRESENT IN BOTH MARKDOWN AND CONTRACT")
Z = 1.959963985
E = c["endpoints"]
CONSTS = [
 ("delta_cross",      E["P2_cross_field"]["delta_cross"],  0.02,  ["delta_cross = 2%", "`delta_cross = 2%`"]),
 ("z_cross",          E["P2_cross_field"]["z_cross"],      Z,     ["1.959963985"]),
 ("delta_abs",        E["P3_absolute"]["delta_abs"],       0.05,  ["delta_abs = 0.05"]),
 ("z_abs",            E["P3_absolute"]["z_abs"],           Z,     ["z_abs = 1.959963985"]),
 ("alpha_geom",       E["P1_geometry"]["alpha_geom"],      0.005, ["alpha_geom = alpha_1 + alpha_2 = 0.005"]),
 ("alpha_1",          E["P1_geometry"]["alpha_1"],         0.004, ["alpha_1 = 0.004"]),
 ("alpha_2",          E["P1_geometry"]["alpha_2"],         0.001, ["alpha_2 = 0.001"]),
 ("theta_cap_deg",    c["mode_resolution"]["theta_cap_deg"],5.0,  ["theta_cap = 5 degrees", "`theta_cap = 5"]),
 ("pipeline target",  c["complete_pipeline"]["target_true_bridge_success"], 0.90, [">= 90%"]),
 ("reported bound",   c["complete_pipeline"]["reported_lower_bound"], 0.9055, ["0.9055"]),
 ("rank_tol",         c["refusal_semantics"]["rank_tol"], 1e-12,  ["rank_tol = 1e-12"]),
 ("sigma_k",          c["hypothetical_uncertainty_scenario"]["sigma_k"], 0.0034, ["0.34%"]),
 ("sigma_cm",         c["hypothetical_uncertainty_scenario"]["sigma_cm"], 0.0115, ["1.15%"]),
 ("T_total_s",        c["hypothetical_uncertainty_scenario"]["T_total_s"], 240.0, ["240 s"]),
]
for name, got, want, needles in CONSTS:
    num_ok = abs(got - want) < 1e-12 or got == want
    md_ok  = any(n in md for n in needles)
    chk(f"{name}: contract == {want}", num_ok, f"contract={got}")
    chk(f"{name}: present in design markdown", md_ok, " | ".join(needles[:1]))

print("\n4. BUDGET ARITHMETIC IS INTERNALLY CONSISTENT")
bt = c["complete_pipeline"]["budget_terms"]
tot = sum(bt.values())
chk("1 - sum(budget terms) == raw_union_expression",
    abs((1 - tot) - c["complete_pipeline"]["raw_union_expression"]) < 1e-8,
    f"1-{tot:.8f} = {1-tot:.8f}")
chk("reported_lower_bound == round(max(0, raw), 4)",
    abs(round(max(0.0, c["complete_pipeline"]["raw_union_expression"]), 4)
        - c["complete_pipeline"]["reported_lower_bound"]) < 1e-12)
chk("4 x alpha_geom term matches alpha_geom", abs(bt["4x_alpha_geom"] - 4*E["P1_geometry"]["alpha_geom"]) < 1e-12)
chk("alpha_1 + alpha_2 == alpha_geom",
    abs(E["P1_geometry"]["alpha_1"] + E["P1_geometry"]["alpha_2"] - E["P1_geometry"]["alpha_geom"]) < 1e-12)
chk("raw union expression exceeds the 0.90 target",
    c["complete_pipeline"]["raw_union_expression"] >= c["complete_pipeline"]["target_true_bridge_success"])

print("\n5. THE SUPERSEDED FIXED-B0 RULE HAS NOT RETURNED")
chk("contract lists fixed-B0 as forbidden",
    any("fixed_B0" in f for f in c["forbidden_mechanisms"]))
chk("design markdown marks fixed-B0 forbidden",
    "fixed-`B0` normalisation" in md and "**forbidden**" in md)
chk("no authorised occurrence of V = Delta U / B0",
    "V = Delta U / B0" not in md.replace("(`V = Delta U / B0`, giving", ""))

print("\n6. NO POWER-SPECTRUM / CORNER-FREQUENCY BRANCH-A CALIBRATION IS AUTHORISED")
fb = c["information_separation"]["forbidden_branch_A_routes"]
au = c["information_separation"]["authorised_branch_A_routes"]
chk("power-spectrum route listed forbidden", any("power_spectrum" in x for x in fb))
chk("corner-frequency route listed forbidden", any("corner_frequency" in x for x in fb))
chk("equipartition route listed forbidden", any("equipartition" in x for x in fb))
chk("corner-frequency NOT in the authorised list", not any("corner" in x for x in au))
chk("power-spectrum NOT in the authorised list", not any("spectrum" in x for x in au))
chk("authorised list is exactly the two mechanical/thermometry routes",
    set(au) == {"force_displacement_with_stokes_drag", "independent_calibrated_thermometry"}, str(au))
chk("design markdown marks corner-frequency FORBIDDEN for E1a",
    "**FORBIDDEN for E1a**" in md and "corner-frequency" in md)
chk("design markdown carries the supersession notice",
    "SUPERSESSION NOTICE" in md and "8c48103" in md)

print("\n7. NO TOTAL-ENTROPY-PRODUCTION OVERCLAIM IN ACTIVE BASELINE E1a TEXT")
chk("'Delta S_total' absent from the baseline", "Delta S_total" not in bl)
chk("'total entropy increase' absent from the baseline", "total entropy increase" not in bl)
chk("baseline states Delta s_tot = 0", "Delta s_tot = 0" in bl)
chk("baseline states Delta s_med = + k_B E_theta", "Delta s_med = + k_B E_theta" in bl)
chk("baseline states Delta s_sys = - k_B E_theta", "Delta s_sys = - k_B E_theta" in bl)
chk("baseline carries the explicit prohibition",
    "NOT total stochastic entropy production" in bl)
chk("baseline keeps the four objects distinct",
    "four different" in bl and "never equated" in bl)
chk("contract prohibition present",
    c["entropy_semantics"]["prohibited"].startswith("kB E is NOT total stochastic entropy production"))
chk("contract lists the four distinct objects",
    len(c["entropy_semantics"]["four_objects_never_equated"]) == 4)

print("\n8. P4 CLASSIFIED AS A DETERMINISTIC CHECK, STILL MANDATORY")
P4 = E["P4_entropy"]
chk("P4 mandatory", P4["mandatory"] is True)
chk("P4 classified deterministic", P4["classification"] == "DETERMINISTIC PHYSICAL/THEORETICAL CONSISTENCY CHECK")
chk("P4 does not read Branch-B data", P4["reads_branch_B_data"] is False)
chk("P4 contributes zero stochastic failure probability", P4["stochastic_failure_probability_after_passing"] == 0.0)
chk("P4 budget term is zero", bt["P4_failure"] == 0.0)
chk("design markdown carries the same classification",
    "DETERMINISTIC PHYSICAL/THEORETICAL CONSISTENCY CHECK" in md)

print("\n9. THE 0.9055 QUALIFICATIONS ARE RECORDED, NOT OMITTED")
cp = c["complete_pipeline"]
chk("not claimed as demonstrated empirical power", cp["is_demonstrated_empirical_power"] is False)
chk("not claimed as an unconditional lower bound", cp["is_unconditional_lower_bound_on_implemented_pipeline"] is False)
chk("union inequality labelled an exact theorem", "EXACT THEOREM" in cp["union_inequality_label"])
chk("all four standing qualifications present", len(cp["standing_qualifications"]) == 4)
chk("required interpretation says validation remains mandatory",
    "remains mandatory" in cp["required_interpretation"])
chk("design markdown carries the required interpretation verbatim",
    "does not certify achieved" in md and "remains **mandatory**" in md)
chk("scenario labelled sufficient, not necessary",
    "SUFFICIENT" in c["hypothetical_uncertainty_scenario"]["sufficiency"].upper()
    and "NOT demonstrated necessary" in c["hypothetical_uncertainty_scenario"]["sufficiency"])

print("\n10. FINITE-BATH UNITS CORRECTION APPLIED")
fbr = c["entropy_semantics"]["finite_bath_remainder"]
chk("1 mm^3 == 1 uL == 1e-9 m^3", fbr["volume_m3"] == 1e-9 and "EXACTLY" in fbr["volume_note"])
chk("heat capacity is sourced, not 3 N k_B", "CRC" in fbr["source"] and fbr["water_c_p_J_per_g_K"] == 4.1816)
chk("remainder is not a statistical endpoint", fbr["is_statistical_endpoint"] is False)
chk("design markdown carries the correction notice", "CORRECTION NOTICE" in md and "1 mL" in md)

print("\n11. AUTHORIZATION BOUNDARIES ARE CLOSED")
ab = c["authorization_boundaries"]
chk("analytical design ADOPTED", ab["analytical_design"] == "ADOPTED")
chk("implementation NOT STARTED", ab["bounded_implementation"] == "NOT STARTED")
chk("synthetic validation NOT STARTED", ab["synthetic_validation_campaign"] == "NOT STARTED")
chk("preregistration NOT AUTHORISED", ab["preregistration"] == "NOT AUTHORISED")
chk("physical execution NOT AUTHORISED", ab["physical_execution"] == "NOT AUTHORISED")
chk("baseline status reflects adoption, not validation",
    "v4 DESIGN ADOPTED" in bl and "NOT** empirically passed validation" in bl)
chk("baseline no longer claims 'no new design decision is required'",
    "**No new design decision is required.**" not in bl)

print("\n" + "="*76)
print(f"  {checks - len(fails)} / {checks} checks passed")
if fails:
    print("  FAILED:"); [print("    -", f) for f in fails]
print("="*76)
sys.exit(1 if fails else 0)
