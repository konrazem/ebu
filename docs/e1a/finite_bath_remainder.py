"""E1a v4 - finite-reservoir remainder on the constrained-macrostate entropy.

DETERMINISTIC ONLY: closed-form arithmetic. No RNG, no trajectories, no model state.
Corrects two errors in the superseded scratch calculation (E1A_V4_REPORT.md, commit
8c48103, Part I section 5.1 / Part IV "corrections" transcript):
  (1) 1 mm^3 and 1 uL were treated as DIFFERENT volumes; they are equal.
      The row labelled "1 uL" used 1e-9 * 1e3 m^3 = 1e-6 m^3, which is 1 mL.
  (2) the heat capacity of LIQUID water was estimated by a generic 3 N k_B
      (Dulong-Petit, a solid-lattice estimate), which is not justified here.

This quantity is NOT an E1a statistical endpoint. It exists only to show the scale of
the finite-bath correction to the constrained-macrostate reading of k_B E.
"""
import math

kB = 1.380649e-23                 # J/K, SI defining constant

# ------------------------------------------------------------------ A. symbolic form
# Bead held at x; reservoir holds E_tot - U(x). With dS/dE = 1/T and d2S/dE2 = -1/(T^2 C):
#     S_constr(x) = S_res(E_tot) - U(x)/T - U(x)^2/(2 T^2 C) + ...
#     Delta S_constr = k_B E_theta + remainder
#     remainder / leading = U / (2 T C)                 <- EXACT to this order, symbolic in C
print("A. SYMBOLIC (option A of the review): remainder/leading = U / (2 T C), C the")
print("   reservoir heat capacity at constant volume. No numerical value is required for")
print("   the E1a design; the expression alone shows the correction vanishes as C grows.\n")

# ------------------------------------------------- B. one sourced macroscopic value
# Liquid water at 298.15 K, standard reference values:
#   density              rho = 997.0 kg m^-3
#   specific heat (c_p)  4.1816 J g^-1 K^-1
# Source: CRC Handbook of Chemistry and Physics, 97th ed., "Thermophysical Properties
# of Water"; equivalently NIST Chemistry WebBook, water, liquid phase, 25 C.
# c_v for liquid water at 298 K is ~4.13 J g^-1 K^-1, i.e. c_p and c_v differ by ~1%.
# That 1% is irrelevant at the magnitude computed below; c_p is used and the choice stated.
RHO   = 997.0
C_P   = 4.1816
T     = 298.15
VOL   = 1e-9                      # m^3.  1 mm^3 = 1 uL = 1e-9 m^3  EXACTLY.
E_EBU = 5.0                       # the worked example used throughout the programme

mass_g = RHO * VOL * 1e3          # kg -> g
C_JK   = C_P * mass_g             # J/K
C_kB   = C_JK / kB                # dimensionless
rem    = E_EBU / (2.0 * C_kB)     # U = E * k_B T  =>  U/(2 T C) = E k_B /(2 C) = E/(2 C/k_B)

print("B. ONE SOURCED VALUE (option B of the review)")
print(f"   volume                1 mm^3 = 1 uL = {VOL:.3e} m^3   (identical volumes)")
print(f"   density               rho   = {RHO} kg m^-3        [CRC 97th ed., water, 25 C]")
print(f"   specific heat         c_p   = {C_P} J g^-1 K^-1  [CRC 97th ed., water, 25 C]")
print(f"   mass                        = {mass_g:.6f} g")
print(f"   heat capacity         C     = {C_JK:.6e} J/K")
print(f"   C / k_B                     = {C_kB:.6e}")
print(f"   remainder/leading at U = {E_EBU:.0f} k_B T  =  E/(2 C/k_B) = {rem:.4e}")
print()
print(f"   SUPERSEDED VALUE, for the record: the scratch calculation reported 2.491e-20")
print(f"   for '1 mm^3' using C/k_B = 3 N k_B = 1.004e20, and a second row labelled '1 uL'")
print(f"   that was in fact 1 mL. Corrected C/k_B is {C_kB:.4e}, a factor {C_kB/1.004e20:.3f} larger,")
print(f"   and the corrected remainder is {rem:.4e}.")
print()
print("   CONCLUSION, unchanged in substance: the finite-bath correction is ~1e-20 for any")
print("   macroscopic reservoir, so Delta S_constr = k_B E holds to first order in U/(T C).")
print("   The correction changes the number, not the conclusion. NOT a statistical endpoint.")
