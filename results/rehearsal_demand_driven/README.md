# Demand-driven rehearsal artifact

**CLASS: REHEARSAL / NON-CONFIRMATORY. NOT SCIENTIFIC EVIDENCE.**

`DEMAND_DRIVEN_REHEARSAL.json.gz` is the output of `demand_driven_rehearsal.py`
for model `EBU-DEMAND-DRIVEN-ECONOMY-v1`. It exists to show that the machinery
runs end to end and replays exactly, and for nothing else.

No hypothesis is registered here, no comparison is preregistered, no seed is
selected, and no number in this artifact may be cited as a finding about
whether the demand-driven economy restores, is safe under a hostile actor, or
differs from its comparator. The model is not tuned to anything in it.

What it does establish, and all it establishes:

- 3,200 epochs across four policies and four replicates complete without
  refusal;
- the replay reproduces every scientific column exactly;
- the package code identity is unchanged between the run and the replay;
- accounting, conservation, nonnegativity, separability and capacity-source
  residuals are all exactly zero, with tolerance literally zero;
- the economic arrival sequence is identical under all four policies, as the
  stream-separation contract requires.

It additionally carries the checks required by the audit correction pass, all
of which are semantics checks rather than observations:

- zero economic double-service events — no coordinate ever had served orders
  claiming more than the pool actually delivered;
- zero economic demands served more than once;
- zero executed actions without demand provenance;
- identical raw arrival sequences across arms, with admitted counts differing
  by arm, which is the endogenous-admission contract working;
- the full arrival lifecycle over the common raw arrival set, so no comparison
  need ever be computed over admitted demands alone.

It also reports the two search statuses introduced with the plan-cap
disposition, `SEARCH_INCOMPLETE_AT_PLAN_CAP` and `SEARCH_BUDGET_EXCEEDED`, and
warns if the status counts fail to cover every epoch. The cap is a
computational enumeration limit, so an empty menu attributable to it is
reported as a search limitation and never as physical impossibility.

## The Study-1 block

The artifact carries a second, separate rehearsal under the key `study_one`.
It runs the frozen-domain world `study-one-v1`
(`DEMAND_DRIVEN_STUDY_ONE_DOMAIN.md`) with **registered failure semantics on**
— an undecided search would raise `JobInvalid` and stop the job rather than be
recorded — and with the **decomposition gate on**, so every epoch
independently verifies the component path against the decomposition-free
**policy-conditioned** reference at four levels: physical eligibility, the
affordable set under that arm's own balances, the selection law the policy
induces over canonical plan identities, and the modeled-outcome law it pushes
forward.

The reference is progress semantics, not "one plan serving every active
demand". A part proved impossible is `BLOCKED`; a part whose every plan is
EBU-unaffordable is `UNAFFORDABLE`; both contribute no action and leave their
demands pending, and every other part contributes exactly one plan chosen by
the policy. The narrower all-demands-complete query still exists under its own
name and is explicitly not runtime semantics — conflating the two made the old
comparison pass vacuously whenever any component was blocked.

The physical layer alone is **not** a runtime verification: an EBU arm never
samples from it, and the comparator deliberately does.

It establishes, and only establishes: 3,200 epochs complete, the replay is
exact, every residual is exactly zero, `SEARCH_UNRESOLVED` occurred zero times
and `SEARCH_INCOMPLETE_AT_PLAN_CAP` zero times — both of which the domain
makes impossible by construction rather than merely rare — and the component
path matched the progress reference at all four levels in every epoch that
had anything to decompose.

The general `sandwater-v1` block above is **not** a Study-1 world: its
plan-size cap binds and it carries two resources. Its
`SEARCH_INCOMPLETE_AT_PLAN_CAP` counts are therefore expected and are a
property of that exploratory world, not of the frozen domain.

Artifacts from the superseded builds at commits `22fd229` and `e37e868` were
**replaced**, not amended. The first mis-counted additive economic service;
the second derived coupling from padded plans, so physically unusable routes
could destroy serviceability. No number from either is citable, even as an
infrastructure observation.

Registered artifacts live in `results/stage_a/`, `results/stage_b/` and
`results/homeostasis/`. This directory is not one of them.
