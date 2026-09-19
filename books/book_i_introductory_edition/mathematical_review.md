# Mathematical review notes

Scope: new Book I exposition and invented fixed teaching states. The review
uses exact algebra, dimensional analysis and rational arithmetic. It does not
run a scientific engine, advance a model state, estimate a parameter or test
empirical behaviour. `verify_mathematics.py` imports only the standard library;
its 86 checks are reported individually in `review/mathematics_checks.json`.
Source passage locks and limitations are in `claim_source_ledger.md` (M01-M11).

## Definitions, units and elementary derivations

1. **Physical world (8.1-8.4).** Source minus finite quantity and destination
   plus that same quantity cancel in the mass sum. The litre illustration
   assumes homogeneous water and fixed conditions. Nonnegativity, storage
   capacity and any route constraints are separate requirements. A rate times
   duration is a quantity: 2 L/min times 1.5 min is 3 L, not 3 L/min.
2. **Reference (10.1).** Nonnegative references summing to the fixed mass, with
   each reference within its declared capacity, place the reference inside
   this domain. They do not establish reachability under an action menu. The
   12/12 target is incompatible with mass 20. Positive scales are mandatory.
3. **Quadratic ruler (11.1).** The stock displacement divided by a stock scale
   is dimensionless. Squaring gives a nonnegative local score, zero exactly at
   the reference. The one-half convention simplifies differentiation. The
   relative-log-density identity (11.4) follows by cancellation of the normal
   density's prefactor and `-log(exp(-V)) = V`. It uses a dimensionless ratio,
   not the logarithm of a dimensional density. No empirical normality follows.
4. **Sum and support (12.1-12.2).** Splitting the fixed sum into affected and
   unchanged terms proves cancellation. For coupled factors the affected set
   must include all changed factors and their evaluation dependencies. The
   four-cell example has potential 5 before and 1.25 after; its unaffected
   contribution is exactly 1 on each side. No world scan or actor optimiser is
   required by this algebra.
5. **Marginal (13.1).** Expanding `(d+h)^2-d^2` gives `2dh+h^2`; division by
   `2 sigma^2 h` and the limit `h -> 0` yields `mu=d/sigma^2`. Its unit is
   inverse stock. The vector direction has entries -1,+1. Thus the directional
   marginal reduction is `-mu^T S = mu_i-mu_j`. A derivative does not choose a
   rate or action. The 0.1 L local sensitivity example gives exactly -0.09875.

## Finite actions, groups and path accounting

6. **Exact finite expansion (14.3).** Expanding every fixed quadratic factor
   yields `V(x+delta)=V(x)+mu^T delta+(1/2)delta^T H delta`, where diagonal
   entries of H are `1/sigma_i^2`. Negation yields the displayed field value.
   H has inverse-square-stock units, so both terms have account units. It is
   positive definite for finitely many positive scales; the curvature
   correction is strictly positive for a nonzero net increment. This is exact
   algebra, not a statement about physical measurement accuracy.
7. **Transfer (14.4).** Substitution of `delta=q(-e_i+e_j)` produces
   `q f_e - q^2(1/sigma_i^2+1/sigma_j^2)/2`. With the declared scales this is
   `2q-q^2/4` for q numerically expressed in litres. Every row of the seven-row
   table has separately checked mass, capacity, endpoint arithmetic, potential
   and value. These are alternatives at one start, never a generated series.
   The maximum at q=4 is geometric information, not an actor selection rule.
8. **General account (15.1).** The endpoint difference is taken against the
   frozen action baseline and complete affected support. C is nonnegative and
   in compatible account units, zero for genuine no action. C=0 is restricted
   to the ideal illustration. The manuscript preserves the unresolved
   historical partially represented dissipation issue and adopts no lossy
   coefficient. The same effect cannot be recharged through a residual term.
9. **Group interaction (16.1-16.2).** For fixed additive increments, expanding
   the joint square gives `E_ab=E_a^0+E_b^0-delta_a^T H delta_b`. Symmetry of H
   combines the two mixed terms. The correction can have either sign; it is
   not a universal subadditivity claim. The three-tank example has initial V=7,
   singleton endpoint V=3 and V=4, and joint endpoint V=1. Thus 6=4+3-1.
   Fixed-increment algebra is not applied to a quantity-changing resolver.
10. **Path identity (16.3).** The chain rule and fundamental theorem of calculus
    for a fixed C1 potential on the declared segment give the exact integral.
    Lambda is dimensionless interpolation, not automatically physical time.
    For a quantity path, s has stock units and the integral of f ds has account
    units. Convex stock bounds do not establish every physical path constraint.
11. **Attribution (16.4-16.5).** Replace the group's increment in the final dot
    product with each fixed child's increment and sum; linearity establishes
    closure. Integrating the affine quadratic gradient gives
    `R_a=-mu^T delta_a-(1/2)delta_a^T H delta_G`. The numerical contributions
    3.5 and 2.5 sum to 6. Sequential allocations (4,2) and (3,3) also total 6,
    while naming different histories. No entitlement, causal identification,
    physical path or spending permission follows from the chosen allocation.
    The historical Aumann-Shapley relationship is expressly acknowledged.

## Sequences and prospective bookkeeping

12. **Telescoping (17.1).** Consecutive endpoints evaluated under one fixed V
    cancel term by term. This is proved directly for authoritative joint
    transitions; it does not silently remove restrictions from a historical
    one-action theorem. Complete relevant state, no duplicated events and no
    unrecorded intervening changes are necessary.
13. **Cycles (17.2).** Equal complete endpoints remove the potential term.
    With nonnegative included process burdens the net is nonpositive. The
    ideal three-litre outward/backward arithmetic totals zero; it is not a
    claim that real pumping consumes no energy. Split process costs may differ.
14. **Drive (17.3).** Insert `V(z^n)-V(x^n)` in each action equation to obtain
    the signed external injection. The plus sign on its cumulative sum is
    correct. No action at the post-drive baseline has zero actor field value.
    Changing the ruler requires a distinct version-change record.
15. **Capacity/audit (17.4).** Under the stated prospective aggregate balance
    and audit definitions, coefficients of `V_next`, `V_z` and `V_old` cancel
    in `V+sum B-J`. Nonnegative affordability, ownership and same-event netting
    require separate rules. The identity assumes C=0 and supplies no recovery,
    borrowing, refill or transferable-pool permission.
16. **Boundedness (17.5).** On `[0,M]`, a squared displacement reaches its maximum
    at an endpoint. Summing individual upper bounds is valid, although possibly
    loose on the fixed-mass simplex. Positive fixed scales and finite references
    make the bound finite. Comparison policies in the same domain inherit it;
    it is not empirical evidence of EBU regulation, stability or attraction.

## Review outcome and open boundaries

The displayed derivations and arithmetic are internally consistent within
their stated scope. No required theorem conflict was found. The claim ledger
deliberately avoids extending historical concavity or one-sign interaction
statements beyond their assumptions. The exact EBU equation is explained as
an account, not a compulsory maximising controller.

Open scientific questions include calibration, adequacy of the physical state,
measurement and verification, the lossy-process valuation boundary, physical
action-time models, ownership, affordability, and empirical recovery. None is
resolved by the illustrations. Author and independent specialist review remain
the next possible stages; neither has been represented as completed here.
