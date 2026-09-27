"""E1a v4 - NON-NORMATIVE EXPLANATORY NOTE: finite-reservoir remainder.

  *** NOT NORMATIVE. NOT A STATISTICAL ENDPOINT. NOT PART OF THE E1a DECISION RULES. ***

The AUTHORITATIVE result is symbolic and lives in
docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md section 9.1:

    Delta S_constr = k_B E_theta + O( U^2 / (T^2 C_V) )
    epsilon_bath   ~  U / (2 T C_V)

This file exists only to show the ORDER OF MAGNITUDE of epsilon_bath for one concrete
macroscopic reservoir. No E1a decision rule depends on any number below.

DETERMINISTIC ONLY: closed-form arithmetic. No RNG, no trajectories, no model state.

------------------------------------------------------------------------------------
ENSEMBLE AND BOUNDARY ASSUMPTIONS (why C_V and not C_P)
------------------------------------------------------------------------------------
  * Composite system: bead + single thermal reservoir, TOTAL ENERGY FIXED (microcanonical
    composite). The reservoir holds E_tot - U(x).
  * The bead is HELD at position x by an external constraint. Its configurational entropy
    at fixed x is a constant independent of x, so it drops out of the difference.
  * The reservoir temperature is DEFINED by  dS/dE|_V = 1/T,  and the second derivative is
    taken AT CONSTANT VOLUME:  d2S/dE2|_V = -1/(T^2 C_V).
  * Both derivatives are therefore constant-volume quantities. **C_V is the correct heat
    capacity; substituting C_P is not licensed by the derivation.**
  * Large-reservoir regime: C_V is finite but C_V >> U/T, which is what makes the
    expansion meaningful.

------------------------------------------------------------------------------------
CORRECTIONS THIS NOTE APPLIES
------------------------------------------------------------------------------------
  (1) docs/e1a/E1A_V4_REPORT.md at commit 8c48103 treated 1 mm^3 and 1 uL as DIFFERENT
      volumes. They are equal: 1 mm^3 = 1 uL = 1e-9 m^3. The row labelled "1 uL" used
      1e-9 * 1e3 m^3, which is 1 mL.
  (2) That same calculation estimated the heat capacity of LIQUID water by a generic
      3 N k_B (Dulong-Petit, a solid-lattice estimate), which is not justified here.
  (3) The first correction pass then used c_P, while the derivation calls for C_V. That
      was internally inconsistent. C_V is derived properly below from the exact
      thermodynamic relation, and the size of the c_P/c_V gap is quantified rather than
      assumed negligible.
"""
import math

kB = 1.380649e-23                 # J/K, SI defining constant

# ---------------------------------------------------------------- A. SYMBOLIC (authoritative)
print("A. AUTHORITATIVE SYMBOLIC RESULT")
print("     Delta S_constr = k_B E_theta + O( U^2 / (T^2 C_V) )")
print("     epsilon_bath   ~  U / (2 T C_V)          C_V at CONSTANT VOLUME, by construction")
print("   No numerical heat-capacity value is required by the E1a design.\n")

# ------------------------------------------- B. one concrete reservoir, C_V derived properly
# Liquid water at 298.15 K. Sourced constants:
#   rho    = 997.0    kg m^-3        density
#   c_P    = 4.1816   J g^-1 K^-1    isobaric specific heat
#   alpha  = 2.57e-4  K^-1           isobaric thermal expansion coefficient
#   kappa_T= 4.525e-10 Pa^-1         isothermal compressibility
# Source: CRC Handbook of Chemistry and Physics, 97th ed., thermophysical properties of
# water at 25 C; kappa_T after Kell (1975), J. Chem. Eng. Data 20, 97. Equivalent values
# appear in the NIST Chemistry WebBook for liquid water at 25 C.
#
# EXACT thermodynamic relation, no approximation:
#     c_P - c_V = T v alpha^2 / kappa_T          v = 1/rho, specific volume
RHO, C_P, ALPHA, KAPPA_T, T = 997.0, 4.1816, 2.57e-4, 4.525e-10, 298.15
VOL   = 1e-9                      # m^3.  1 mm^3 = 1 uL = 1e-9 m^3  EXACTLY
E_EBU = 5.0                       # the worked example used throughout the programme

v_spec  = 1.0 / RHO                                   # m^3 / kg
gap_kg  = T * v_spec * ALPHA**2 / KAPPA_T             # J kg^-1 K^-1
gap_g   = gap_kg * 1e-3                               # J g^-1 K^-1
C_V     = C_P - gap_g                                 # J g^-1 K^-1
mass_g  = RHO * VOL * 1e3
CV_JK   = C_V * mass_g
CV_kB   = CV_JK / kB
eps     = E_EBU / (2.0 * CV_kB)                       # U = E k_B T -> U/(2 T C_V)

CP_JK   = C_P * mass_g
CP_kB   = CP_JK / kB
eps_cp  = E_EBU / (2.0 * CP_kB)

print("B. ONE CONCRETE RESERVOIR - C_V DERIVED, NOT SUBSTITUTED")
print(f"   volume                1 mm^3 = 1 uL = {VOL:.3e} m^3   (identical volumes)")
print(f"   rho                         = {RHO} kg m^-3")
print(f"   c_P                         = {C_P} J g^-1 K^-1")
print(f"   alpha                       = {ALPHA:.3e} K^-1")
print(f"   kappa_T                     = {KAPPA_T:.4e} Pa^-1")
print(f"   c_P - c_V = T v alpha^2/kappa_T = {gap_g:.6f} J g^-1 K^-1")
print(f"   c_V                         = {C_V:.6f} J g^-1 K^-1")
print(f"   c_P / c_V                   = {C_P/C_V:.6f}   ->  c_P exceeds c_V by {100*(C_P/C_V-1):.3f} %")
print(f"   mass of 1 uL                = {mass_g:.6f} g")
print(f"   C_V                         = {CV_JK:.6e} J/K")
print(f"   C_V / k_B                   = {CV_kB:.6e}")
print(f"   epsilon_bath at U = {E_EBU:.0f} k_B T  = E/(2 C_V/k_B) = {eps:.4e}")
print()
print("   SIZE OF THE APPROXIMATION IF C_P WERE USED INSTEAD (it is NOT used):")
print(f"     C_P/k_B = {CP_kB:.6e}   ->  epsilon = {eps_cp:.4e}")
print(f"     relative difference = {100*(eps/eps_cp-1):.3f} %  of an already ~1e-20 quantity.")
print("     Adequate for an order-of-magnitude illustration, but the derivation calls for")
print("     C_V, so C_V is what is reported. The gap is stated, not assumed away.")
print()
print("   SUPERSEDED VALUES, for the record:")
print("     3 N k_B estimate   C/k_B = 1.004e20,  epsilon = 2.491e-20   (unjustified for a liquid)")
print(f"     c_P-based pass     C/k_B = {CP_kB:.4e},  epsilon = {eps_cp:.4e}   (inconsistent with the derivation)")
print(f"     CORRECTED (C_V)    C/k_B = {CV_kB:.4e},  epsilon = {eps:.4e}")
print()
print("   CONCLUSION, unchanged in substance across all three: epsilon_bath is ~1e-20 for any")
print("   macroscopic reservoir, so Delta S_constr = k_B E holds to first order in U/(T C_V).")
print("   The correction changes the number, not the conclusion. NOT a statistical endpoint.")
