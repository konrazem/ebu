# Next-study mechanism alternatives packet

Status: **enumeration only. Nothing here is implemented, adopted, preregistered
or authorized.** No alternative below may be retrofitted into Stage A or Stage B,
whose mechanism, code identity and artifacts are immutable.

Motivation: `STAGE_B_SCIENTIFIC_DISPOSITION.md` section 1.3 — under sustained
conservative forcing the present mechanism's affordability gate weakens
monotonically because curvature-driven potential injection accumulates as
permanent spendable capacity.

## 0. The mechanism to be addressed, stated precisely

For the quadratic potential, `D_ext = mu^T u + (1/2) u^T H u`. The curvature
term is nonnegative and, at the registered `q0 = 1` and `sigma = 1`, exactly
`+1` per applied forcing event. The accounting identity
`V + sum_i B_i = J` then forces `sum_i B_i` to absorb that drift, because
physical conservation bounds `V` by `V_max`.

So the loosening is **not** a tuning artifact. Any alternative must engage one
of exactly four places:

1. the potential (what counts as deviation);
2. the forcing law (what nature injects);
3. the receipt rule (what an action earns);
4. the capacity state law (what a balance does over time).

## 1. Candidate alternatives

Each is a **new model**. None is recommended here.

### A. Capacity decay / demurrage
`B_i <- (1 - lambda) B_i` per tick, or an absolute decrement.

- Question: does a decay rate exist that holds `rho_reject` stationary without
  making the gate trivially binding?
- Risk: **breaks the exact accounting identity.** `V + sum B = J` no longer
  holds; a decay sink must be declared and audited, or the identity must be
  restated as `V + sum B + sink = J`. This is the largest cost: both registered
  studies rest on that identity holding at zero tolerance.

### B. Capacity expiry (aged buckets)
Receipts expire a fixed number of ticks after being earned.

- Question: does bounded-lifetime capacity keep the gate binding indefinitely?
- Risk: same identity breakage as A, plus per-receipt bookkeeping that enlarges
  state and complicates replay. Introduces an arbitrary timescale.

### C. Capacity cap
`B_i <- min(B_i, B_max)`.

- Question: does a cap tied to `V_max` keep the gate binding?
- Risk: identity breakage at the cap, and a new free parameter whose value would
  dominate the result. A cap of `O(V_max)` would likely make the gate strongly
  binding; that must not be chosen by inspecting outcomes.

### D. Relative / normalized affordability
Leave `B` unbounded but make the gate scale-free, e.g. require
`B_i + Delta B_i >= 0` **and** `|Delta B_i| <= kappa * (V + something)`.

- Question: can the gate stay binding without touching the capacity state law?
- Merit: **the only family that need not break `V + sum B = J`**, because it
  changes the admissibility predicate rather than the accounting.
- Risk: a second free parameter `kappa`; and the predicate risks reading global
  `V`, which would violate the locality property the programme has preserved.

### E. Change the forcing law
Use a forcing process whose expected potential injection is zero, e.g. pairing
each increment with its exact inverse, or drawing increments that are
curvature-compensated.

- Question: is the loosening specific to positive-drift forcing?
- Merit: isolates cause cleanly and changes **no** EBU mechanism at all. This is
  the cheapest diagnostic and arguably should precede A–D.
- Risk: a curvature-compensated law is state-dependent, which reintroduces the
  arm-pairing problem Stage B handled with `NULL_FORCING`.

### F. Non-quadratic potential
A potential whose curvature term does not inject positive potential under
conservative transport.

- Question: is the drift an artifact of the Gaussian family specifically?
- Risk: abandons the Level-1 Gaussian direction the whole programme reconciled
  around; large scope, and the historical hinge family is already preserved and
  available for comparison.

## 2. Ordering recommendation

If a next study is authorized, **E before A–D**. E changes no EBU mechanism and
answers whether the loosening is caused by the forcing law's positive drift or
by the capacity rule itself. Redesigning capacity before knowing that would be
treating a symptom whose cause has not been localized.

D is the next cheapest, being the only capacity-side family that preserves the
exact accounting identity.

A, B and C should be considered together and only with an explicit, audited
restatement of the accounting identity, since all three break it.

## 3. Hard constraints on any such study

- Stage A and Stage B artifacts, preregistrations and code identity are
  immutable. A new mechanism gets a new code identity and a new preregistration.
- No alternative may be selected by inspecting Stage-B trajectories beyond the
  registered diagnostics already reported.
- Any parameter (`lambda`, expiry horizon, `B_max`, `kappa`) must be frozen
  before execution and must not be tuned to produce binding behaviour.
- The exactness and replay guarantees demonstrated twice must be preserved, or
  the loss must be stated explicitly and justified.
- EBU must still calculate and not choose. No alternative may introduce
  value-ranked selection.
