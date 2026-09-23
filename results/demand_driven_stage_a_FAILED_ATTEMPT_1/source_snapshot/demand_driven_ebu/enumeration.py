"""Plan enumeration primitives, and the structural reach coupling is built on.

Kept separate from `coupling` and `plans` so the dependency graph stays
acyclic, and because the two use enumeration for different purposes with
different soundness requirements.

## Three route sets, deliberately different

* The **structural reach** is what decides coupling: a set of tokens large
  enough to contain the support of every *minimal* plan serving a
  requirement, derived from the world and the frozen baseline rather than
  from enumerated plans. It is free of the plan-size cap and free of padding.
* The **search routes** are generous: every route touching the transport
  closure of a component's coordinates. Breadth here is safe in the only
  direction that matters -- it can offer more valid plans, never delete one --
  so menus are built over this set.
* **Usable routes** are those that can carry at least one declared quantum. A
  route with capacity below every quantum carries no action and must be
  behaviorally invisible.
* **Live routes** are usable routes whose source can fund their smallest
  usable quantum at the frozen baseline.

## Route liveness

**Necessity (all domains).** If a route `r` carries an action in any
executable plan `G` at state `x`, then `r` is live. The action moves a
declared quantum `q <= cap(r)`, so `r` is usable; and source-funding requires
`x[source(r)] >= sum of everything source(r) sends in G >= q >= min{declared
quanta that fit cap(r)}`. So filtering on liveness removes no route that any
executable plan could use, and the structural reach remains a **sound
superset** of every minimal plan's support in every domain.

**Sufficiency (Study-1 domain only).** In the frozen Study-1 domain -- one
resource, lossless routes, no declared storage capacity, `x >= 0` -- every
live route carries an action in some executable plan, namely the singleton
`{(r, q_min)}`. Its quantum is declared and fits the route capacity; source
funding holds by liveness; the destination only gains, so nonnegativity holds;
there is no storage capacity to exceed; and losslessness closes conservation
exactly. So in Study 1 liveness is **necessary and sufficient**, and the live
route set is exactly the set of routes that can act.

**This sufficiency is claimed for Study 1 and nowhere else.** Outside it the
rule is necessary but not tight, and the reach is a sound superset that can
over-couple:

* a **declared upper storage capacity** on a requirement coordinate activates
  the capacity-relief limb below, so a route out of that coordinate enters the
  reach even when the capacity has no chance of binding
  (`fixtures.capacity_relief_world`, finding F-5);
* a **loss sink** enters the reach as a delivery target, after which every
  route depositing into that sink is pulled in behind it, merging demands that
  share nothing but waste (`fixtures.shared_sink_world`, finding F-6).

A third limb -- destination headroom -- would be needed to tighten the first,
and sinks would need to be excluded from the reach to tighten the second.
Neither is attempted here. Both worlds are refused by
`study_one.require_domain`, both are permanent regressions, and neither is a
blocker to Study 1.

## Why the reach is a sound superset

Let `G` be an irredundant executable plan serving requirement set `R`, and take
`a` in `G`. Irredundancy says `G \\ {a}` either fails to serve `R` or cannot
execute.

*If it fails to serve `R`*, some coordinate `c` of `R` has
`delta_{G\\a}[c] < req(c)` while `delta_G[c] >= req(c)`, so `a` raises the
increment at `c`: `a` **delivers into a requirement coordinate**, either as its
destination or as its loss sink.

*If it cannot execute*, the broken condition can only be the stock capacity at
`a`'s source. Quantum and route-capacity checks are per action and unaffected
by removal; source-funding only relaxes when an outflow is removed; and
endpoint nonnegativity cannot break, because source-funding on `G` gives
`state[i] + delta_S[i] >= state[i] - outflow_G[i] >= 0` for every subset `S`.
Removing `a` removes an outflow from its source, which can only push that
coordinate *up*, so the sole exposure is a declared stock capacity there.

So every action of every minimal plan either delivers into a requirement
coordinate or drains a capacity-bearing coordinate that receives inflow inside
the plan. `structural_reach` closes over exactly those two cases. In the
Study-1 domain no coordinate declares a capacity, so the second case is empty,
the closure is one pass, and the reach is exactly `R` together with the
sources of the live routes delivering into `R`.

## Search completeness

`physically_serviceable` enumerates plans over the live structural-reach
routes, at most one action per route, in increasing size. That pruning is
**equivalent to complete enumeration of the whole finite plan space** for the
existence question it answers. One direction is inclusion. For the other: if
any complete executable plan exists, some minimal such plan `G'` exists, `G'`
is irredundant, so by the paragraph above every action of `G'` lies on a route
of the structural reach, and that route is live because `G'` executes. A plan
uses each route at most once by construction. So `G'` lies inside the pruned
space and is found. The two searches therefore agree on
`SERVICEABLE`/`IMPOSSIBLE` wherever both terminate, and the conformance suite
checks the pruned search against brute force on every fixture.

## The plan-size cap

`world.max_plan_size` is a **computational enumeration limit**, not a physical
simultaneity constraint. See `DEMAND_DRIVEN_PLAN_CAP_DISPOSITION.md`. It
therefore may not decide physical possibility, and nothing here uses it to:
`physically_serviceable` searches without it. A Study-1 world must declare a
cap at least as large as its usable route count, so the cap cannot bind on
anything at all.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product

from gaussian_harness.numerics import Refusal, Vector

from .physical import PhysicalAction, PlanGroup, action_alphabet, can_happen_now
from .service import CoordinateRequirement, served_ids, serves_all, serves_jointly
from .world import DemandWorld, Route

# The uncapped search is bounded by the **work it actually does**, not by a
# worst-case estimate of the space. A pre-check on the space size would refuse
# before trying, turning trivially serviceable requirements into "unresolved"
# whenever the world is wide: nineteen independent one-unit suppliers give a
# space of 2^19 and a plan on the very first evaluation. Enumeration therefore
# proceeds by increasing plan size, returns as soon as a plan is found, and
# spends this budget only on requirements it cannot satisfy.
EXHAUSTIVE_BUDGET = 200_000


def usable_routes(world: DemandWorld) -> tuple[Route, ...]:
    """Routes that can carry at least one declared quantum.

    A route whose capacity is below every quantum carries no action. It must be
    behaviorally invisible: it may not change coupling, serviceability or
    admission, because it cannot change the executable action set.
    """
    return tuple(
        route
        for route in world.routes
        if any(quantum <= route.capacity for quantum in world.quanta)
    )


def live_routes(world: DemandWorld, state: Vector) -> tuple[Route, ...]:
    """Usable routes whose source can fund their smallest usable quantum now.

    **Necessary in every domain**: source-funding requires the source to
    already hold the total it sends, so it must hold at least the smallest
    quantum the route can carry. Filtering on it removes no route that any
    executable plan could use.

    **Sufficient in the Study-1 domain only**, where the singleton plan
    `{(r, q_min)}` is executable for every live `r`. Outside that domain a
    live route may still be unable to act -- a full destination under a
    declared storage capacity is the standing example -- and the reach is then
    a sound superset rather than an exact set. See the module docstring, and
    `study_one` for the boundary.
    """
    live = []
    for route in usable_routes(world):
        smallest = min(
            quantum for quantum in world.quanta if quantum <= route.capacity
        )
        if state[route.source] >= smallest:
            live.append(route)
    return tuple(live)


def search_routes(world: DemandWorld, coordinates: frozenset[int]) -> tuple[Route, ...]:
    """Every route touching the transport closure of these coordinates."""
    closure: set[int] = set()
    for coordinate in coordinates:
        closure |= world.transport_component(coordinate)
    return tuple(
        route
        for route in world.routes
        if route.source in closure or route.destination in closure
    )


@dataclass(frozen=True)
class StructuralReach:
    coordinates: frozenset[int]
    routes: frozenset[str]
    owners: frozenset[str]


def structural_reach(
    world: DemandWorld, state: Vector, requirement_coordinates: frozenset[int]
) -> StructuralReach:
    """Tokens every minimal plan serving this requirement set could bind.

    Built from **live** routes, so a route that can carry no action at this
    baseline -- whether because its capacity is below every quantum or because
    its source is empty -- contributes nothing to coupling.
    """
    usable = live_routes(world, state)
    inflow_targets = set(requirement_coordinates)
    selected: dict[str, Route] = {}
    while True:
        grew = False
        for route in usable:
            if route.route_id in selected:
                continue
            delivers = route.destination in inflow_targets or (
                route.sink is not None and route.sink in inflow_targets
            )
            relieves = (
                route.source in inflow_targets
                and world.coordinates[route.source].capacity is not None
            )
            if delivers or relieves:
                selected[route.route_id] = route
                grew = True
        added = set()
        for route in selected.values():
            added.add(route.destination)
            if route.sink is not None:
                added.add(route.sink)
        if not added <= inflow_targets:
            inflow_targets |= added
            grew = True
        if not grew:
            break

    coordinates = set(requirement_coordinates)
    for route in selected.values():
        coordinates.add(route.source)
        coordinates.add(route.destination)
        if route.sink is not None:
            coordinates.add(route.sink)
    return StructuralReach(
        frozenset(coordinates),
        frozenset(selected),
        frozenset(world.owner_of(route.source) for route in selected.values()),
    )


def _capped_groups(world: DemandWorld, routes, limit: int):
    alphabet = action_alphabet(world, routes)
    for size in range(1, limit + 1):
        for chosen in combinations(alphabet, size):
            if len({action.route.route_id for action in chosen}) != size:
                continue
            yield PlanGroup.of(*chosen)


def exhaustive_space(world: DemandWorld, routes) -> int:
    """Worst-case size of the uncapped per-route search. Reporting only.

    Not used to refuse a search: the search is bounded by the work it does.
    """
    total = 1
    for route in routes:
        total *= 1 + sum(1 for quantum in world.quanta if quantum <= route.capacity)
        if total > 1 << 40:
            return total
    return total


def _sized_groups(world: DemandWorld, routes):
    """Every plan using at most one action per route, in increasing size.

    Size order matters: it puts minimal plans first, so a requirement that has
    any easy answer is answered immediately rather than after a walk through
    the large end of the space.
    """
    per_route = [
        [
            PhysicalAction(route, quantum)
            for quantum in world.quanta
            if quantum <= route.capacity
        ]
        for route in routes
    ]
    populated = [options for options in per_route if options]
    for size in range(1, len(populated) + 1):
        for chosen in combinations(populated, size):
            for combination in product(*chosen):
                yield PlanGroup.of(*combination)


def serving_groups(
    world: DemandWorld,
    state: Vector,
    reqs: tuple[CoordinateRequirement, ...],
    routes,
) -> tuple[PlanGroup, ...]:
    """Complete, executable plans over the given routes, within the cap."""
    return tuple(
        group
        for group in _capped_groups(world, routes, world.max_plan_size)
        if serves_all(reqs, group.increment(world.dimension))
        and can_happen_now(world, state, group).executable
    )


def has_serving_group(
    world: DemandWorld,
    state: Vector,
    reqs: tuple[CoordinateRequirement, ...],
    routes,
) -> bool:
    """Early-exit existence test within the cap.

    Irredundancy is not checked: if any complete executable plan exists then a
    minimal such subset of it is itself complete and executable, so an
    irredundant one exists too.
    """
    for group in _capped_groups(world, routes, world.max_plan_size):
        if not serves_all(reqs, group.increment(world.dimension)):
            continue
        if can_happen_now(world, state, group).executable:
            return True
    return False


SERVICEABLE = "PHYSICALLY_SERVICEABLE"
IMPOSSIBLE = "PHYSICALLY_IMPOSSIBLE"
UNRESOLVED = "SEARCH_BUDGET_EXCEEDED"


def physically_serviceable(
    world: DemandWorld, state: Vector, reqs: tuple[CoordinateRequirement, ...]
) -> str:
    """Whether the requirement set can be served at all, ignoring the cap.

    Exact where it answers at all: minimal plans use only live structural-reach
    routes and at most one action per route, so choosing per route over that
    set is a complete search of the minimal plans.

    Enumeration runs in increasing plan size and returns `SERVICEABLE` on the
    first plan found, so a wide but easy requirement is answered in a handful
    of evaluations rather than refused on the size of its search space. Only an
    unsatisfiable requirement can consume the budget, and exhausting it yields
    `UNRESOLVED` -- never `IMPOSSIBLE`. A negative is reported only when the
    whole space has been enumerated.

    Callers must preserve all three answers. Treating `UNRESOLVED` as
    impossibility would turn a computational limit into a physical claim,
    which is exactly what this three-way return exists to prevent.
    """
    if not reqs:
        return SERVICEABLE
    reach = structural_reach(world, state, frozenset(req.coordinate for req in reqs))
    routes = tuple(route for route in world.routes if route.route_id in reach.routes)
    evaluations = 0
    for group in _sized_groups(world, routes):
        evaluations += 1
        if evaluations > EXHAUSTIVE_BUDGET:
            return UNRESOLVED
        if not serves_all(reqs, group.increment(world.dimension)):
            continue
        if can_happen_now(world, state, group).executable:
            return SERVICEABLE
    return IMPOSSIBLE


def physically_coexistent(
    world: DemandWorld, state: Vector, reqs: tuple[CoordinateRequirement, ...]
) -> str:
    """Can one plan serve every economic claim and progress every physical one?

    The same exact search as `physically_serviceable`, over the same live
    structural-reach routes and with the same three-way return, but asking the
    **conjunctive** question. Used only by admission's protection limb; see
    `service.serves_jointly` for why that question is different from the menu's.
    """
    if not reqs:
        return SERVICEABLE
    reach = structural_reach(world, state, frozenset(req.coordinate for req in reqs))
    routes = tuple(route for route in world.routes if route.route_id in reach.routes)
    evaluations = 0
    for group in _sized_groups(world, routes):
        evaluations += 1
        if evaluations > EXHAUSTIVE_BUDGET:
            return UNRESOLVED
        if not serves_jointly(reqs, group.increment(world.dimension)):
            continue
        if can_happen_now(world, state, group).executable:
            return SERVICEABLE
    return IMPOSSIBLE


def is_irredundant(
    world: DemandWorld,
    state: Vector,
    reqs: tuple[CoordinateRequirement, ...],
    group: PlanGroup,
) -> bool:
    """No proper executable subset already answers everything this plan answers.

    The test is **served-set dominance**, not mere service. A proper subset `S`
    makes `G` redundant exactly when `S` executes and serves every demand `G`
    serves; if `S` serves strictly less, `G` is carrying an action that answers
    something `S` does not, and that action has its own provenance.

    Why it must be stated this way. Under strong atomic provenance a plan
    serves a component when it completely serves every economic claim and
    progresses **at least one** physical claim. A plain "does some subset
    serve?" test would then call every joint plan redundant -- an economic
    order and a physical restoration answered in one epoch would collapse to
    the economic action alone, because that action already "serves". The
    physical need would be made to wait for the economic one, which contract
    section 7 forbids in either direction.

    It is still exactly the guard it was. An action bolted onto a legitimate
    plan answers nothing new, so dropping it preserves the served set and the
    padded plan is refused. Every proper subset is checked, not only the
    single-action removals.
    """
    actions = group.actions
    answered = set(served_ids(reqs, group.increment(world.dimension)))
    for size in range(len(actions)):
        for chosen in combinations(actions, size):
            smaller = PlanGroup(tuple(chosen))
            increment = smaller.increment(world.dimension)
            if not serves_all(reqs, increment):
                continue
            if not answered <= set(served_ids(reqs, increment)):
                continue
            if can_happen_now(world, state, smaller).executable:
                return False
    return True


def irredundant_serving_groups(
    world: DemandWorld,
    state: Vector,
    reqs: tuple[CoordinateRequirement, ...],
    routes,
) -> tuple[PlanGroup, ...]:
    return tuple(
        group
        for group in serving_groups(world, state, reqs, routes)
        if is_irredundant(world, state, reqs, group)
    )
