# Current model

This is the implementation specification for the owner's economic-cell research model. Its assumptions are explicit; it does not establish universal physical calibration or adopt an experimental actor policy.

## Cell state and design

For each cell i:

- x_i is the current compatible resource coordinate, in J.
- x_i* is its reference, in J.
- K_i > 0 is stiffness, in 1/J.
- Phi_i = K_i (x_i - x_i*)^2 / 2 is the imbalance field, in J.
- m_i = K_i (x_i - x_i*) is the current dimensionless slope.
- c_i = 1/K_i is the response scale, in J.

The resource-to-joule mapping must be declared for an application. Different resources are not interchangeable merely because their coordinates use the same unit.

The baseline complete field is the sum of the independent cell fields. Changing another cell alone does not change cell i's marginal. Economic interactions occur through actual resource actions and transfers of existing EBU.

Ordinary actions keep x_i*, K_i and any declared design limits fixed.

## Denomination and contributions

W_Cs = 6.091102297113866550e-24 J per EBU.

For an identified current resource change dx_i:

    dE_i = -m_i dx_i / W_Cs

For an identified finite single-cell change q, with fixed design:

    E(q) = -(m_i q + K_i q^2 / 2) / W_Cs

For a complete finite change:

    E_complete = (Phi_before - Phi_after) / W_Cs

The finite identity checks complete accumulated contributions. It does not identify their actor shares from endpoints alone.

Parallel changes use one current field and a complete, nonduplicated decomposition. If a finite joint event has no specified contribution decomposition, return its complete value without inventing individual credits.

Under the owner's after-action working ideal, complete qualified changes update accounts exactly once. With all relevant contributions included, total existing EBU G satisfies:

    W_Cs * Delta G = -Delta Phi_total

Transfers of existing EBU subtract and add equal amounts. They change holdings, not source attribution or the cell field. Financial claims are separate from existing spendable units.

## Neutral subdivision and composition

For fractions alpha_i > 0 summing to one:

    x_i = alpha_i x
    x_i* = alpha_i x*
    K_i = K / alpha_i

Resource, reference, complete field and inverse stiffness are preserved:

    sum x_i = x
    sum x_i* = x*
    sum Phi_i = Phi
    sum 1/K_i = 1/K

For an equal-slope combination:

    x_new = sum x_i
    x_new* = sum x_i*
    1/K_new = sum 1/K_i

Combining unequal conditions requires representing their remaining difference or performing a permitted operation that removes it. For two cells:

    Phi_A + Phi_B = Phi_aggregate + (m_A - m_B)^2 / [2(K_A + K_B)]

A new name or boundary cannot erase the second term.

An exact split/merge reversal restores the original parameters. No closed sequence restoring the complete state has positive complete signed gain.

## Explicit application constraints

An application may declare indivisible resource units epsilon > 0, usable stock/capacity bounds, source provision and delivery limits. These describe permitted resource operations, not additional EBU fees.

For a whole-unit single-cell change, neither permitted addition nor removal lowers the field when:

    |x - x*| <= epsilon/2

A reference need not be an integer multiple of epsilon unless an application adopts and justifies that requirement.

Power P and available duration T imply a necessary delivered-amount bound P*T. Storage and delivery capability are distinct. Splitting does not automatically multiply source supply, capacity or power.

A size-dependent handling equation is a separately declared model. The explored H(s) = min(eta*s, H_max) is a candidate, not a universal default.

## Three distinct graph meanings

Payment edges describe permitted transfers of existing EBU. Resource-action edges describe permitted physical resource changes. Grouping trees describe composition or origin. One graph does not silently grant the operations of another.

For an allowed resource transfer A to B, current affinity is m_A - m_B. It is a valuation per resource amount, not an action rate.

Any least-resource path comparison must declare its independent resource-use measure and constraints. No universal shortest-path or Fibonacci optimum follows from field conservation alone.
