# Structural findings from implementing the demand-driven model

**Status: STRUCTURAL CONSEQUENCES OF THE FROZEN CONTRACT, NOT BEHAVIOURAL
EVIDENCE.** Each item below is a property of the declared semantics,
demonstrated exactly on a small declared fixture. None is a finding about how
the demand-driven economy behaves in general, none is generalizable from the
fixture it is shown on, and none may be cited as a result. No registered study
of this model exists.

Nothing here is repaired. Repairing any of them would be a model redesign,
which this task explicitly excludes. They are recorded so the first registered
study is designed with them visible rather than discovered mid-run.

---

## F-1 Complete service plus coupling means one stuck obligation freezes its component

A plan must serve **every** demand in its component completely. If any single
demand in a component is unserviceable, the component's menu is empty, and the
serviceable demands in it go unserved too.

**Exact demonstration.** In `sandwater-v1` at state `(8, 12, 10, 6, 6)` the
physical shortfall `P:sand|A` has **5** complete executable plans on its own.
Introduce one admitted economic demand for 25 units of sand — beyond what the
quanta and plan-size cap can deliver — and the coupled component's menu drops
to **0**. The physical need is now unserved, not because anything about it
changed, but because it shares a resource with an obligation that cannot be met.

**Why admission does not prevent it.** Admission refuses an arrival that is
unserviceable *at the moment of admission*, and refuses one that would newly
break an existing obligation. It cannot bind the future: a natural
disturbance, an irreversible loss, or the actor's own previous choice can all
make an already-admitted demand unserviceable afterwards. Contract section 9
accepts blocking *within* a component — it only forbids blocking across
independent ones — so this is faithful, not a bug.

**What it means for study design.** A long registered run can enter a state
where a resource is permanently frozen by one stuck obligation. Whether that
happens, how often, and under which arrival law is an empirical question the
first study must be able to detect, which requires the stuck-component status
to be a reported metric rather than an incident.

**Candidate remedies, all out of scope here.** Demand expiry; partial service
with backlog; splitting a component when a member is provably unserviceable;
an admission rule with a serviceability horizon. Each changes the frozen
service contract and needs its own authorization.

## F-2 Irreversible loss makes complete restoration permanently impossible

Every action conserves quantity over all coordinates, so loss does not destroy
quantity — it moves it somewhere it cannot come back from. In a closed world
the represented stock total then falls permanently below the reference total,
and **at least one shortfall can never be closed**. P-demand at that coordinate
is therefore permanent.

This is not a defect in the loss accounting; it is what irreversibility means
in a conserved world. It does interact with the mandatory-action rule in a way
worth stating.

**Exact worked example, on the `loss-v1` fixture only.** After the economic
action of contract section 28 wastes two units, the reachable potential floor
is exactly `3` — verified by enumerating every executable plan. But the floor
state `(9, 9, 10)` still carries two shortfalls of one unit each, and serving
both completely requires two units drawn from the third cell, which lands at
`V = 4`. Under mandatory complete service the system therefore **leaves** the
floor whenever it reaches it:

> the mandatory-action rule plus complete service produces a recurrent level
> strictly above the reachable potential floor.

Driving the fixture for twelve epochs with no disturbance and no arrivals, the
aligned policy sits at `V = 4` throughout, never visiting `3`.

**Illustrative only.** The other policies on the same twelve epochs show
oscillation and, for the no-EBU comparator, escalation followed by a jammed
`NO_COMPLETE_PHYSICAL_PLAN`. These are single deterministic paths on one
four-coordinate fixture with one lossy route. They are not evidence about
hostile safety, comparator behaviour or anything else, and must not be quoted
as such. They are recorded because they show the mechanism is *capable* of
these regimes, which is what a study must be powered to distinguish.

**Design consequence.** The contract's `eta = 1` baseline is doing real work.
A lossy registered study is a different scientific object from a lossless one,
because in the lossy world the reference is unreachable by construction and
"restoring tendency" has to be redefined against the reachable floor rather
than against `x*`. That redefinition does not exist yet and is a prerequisite
for any lossy study.

## F-3 Consumption is financed per owner by prior restoration

At `B_i = 0` a negative-EBU plan is unaffordable, and there is no pooling,
borrowing or transfer. An economic action that moves the system away from its
reference can therefore only ever be taken by an owner that has **already**
earned capacity by moving it toward the reference.

This is Capacity V1 working as declared rather than a surprise, but it has a
consequence the earlier arbitrary-action studies could not exhibit: in the
demand-driven economy, **which** economic demands can be served depends on
*which node* happens to hold capacity, not on aggregate wealth. The conformance
gate shows a plan being refused to a poor owner while an identical plan from a
richer owner is affordable, with the EBU value identical in both cases.

**Design consequence.** The first registered study's arrival law must declare
its destination distribution deliberately, because an arrival law that
concentrates demand on nodes that never earn will report unaffordability that
is an artefact of the destination distribution rather than of the mechanism.
This is recorded as an unresolved load parameter in the decision packet.

## F-4 Admission's serviceability test is one-epoch and state-dependent

The admission rule asks whether the obligations are serviceable **now**, in the
current physical state, in one epoch. It does not ask whether they could be
served eventually, and it cannot, because the frozen contract has no notion of
service across epochs.

Two consequences follow. An arrival that is briefly unserviceable is rejected
outright rather than deferred — there is no deferral in the model. And because
the test reads the physical state, the *number of admitted demands* legitimately
differs between actor policies even though the *arrival sequence* is identical
across them. The rehearsal shows exactly this: 404 identical arrivals under all
four policies, but 152 to 309 admissions depending on the policy. That is not a
stream leak; it is admission responding to the physical state the policy
produced. The stream-separation property that must hold, and does, is that the
arrival sequence itself is untouched.

---

## What would change these

F-1 and F-4 are consequences of complete-service semantics. F-2 is a
consequence of conservation plus irreversibility. F-3 is a consequence of
Capacity V1's no-pooling rule. Each would be altered only by changing the
corresponding frozen rule, which is a redesign and is not authorized here.
