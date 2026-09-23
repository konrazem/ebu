"""The frozen physical domain of the first demand-driven registered study.

Study 1 is deliberately narrow. Everything the general framework can express
but the first study does not need is pushed outside the boundary and declared
**FUTURE UNSUPPORTED PHYSICS**, so that the completeness claims made for
Study 1 are provable rather than hopeful. Being outside the boundary is not a
defect and not a blocker: it is a statement about what has been proved.

## The frozen domain

A world is a Study-1 world exactly when all of the following hold. The first
group is physics, the second is what makes exhaustive search provable.

**Physics.**

1. one homogeneous scalar resource;
2. every coordinate is a stock carrying a declared reference and scale;
3. no upper destination-storage capacity anywhere;
4. no irreversible sink coordinate;
5. every route lossless, `eta = 1`;
6. no route declares a loss sink;
7. finitely many declared action quantities, all positive;
8. fixed topology -- `DemandWorld` is frozen and no model path mutates it.

`x_i >= 0` and `sum_i x_i = M` are state facts rather than world facts. They
are enforced on every transition by `physical.can_happen_now` and audited to
exactly zero residual every epoch by the harness; `state_violations` checks
them for a given state.

**The two demand classes do not share a completion contract, and never did
need to.** Economic service is complete-service only: an economic order is an
exogenous obligation whose residual would have to be stored against its id, so
partial fulfilment would require a backlog quantity. Physical service is
atomic: a shortfall is re-derived from the state every epoch, so incremental
restoration needs no record and a plan serves a physical demand exactly when it
makes genuine positive progress on it.

No E backlog quantity, no P queue, no deadline and no service order are
structural: nothing in the package implements any of them, and the conformance
suite asserts their absence. The atomic P rule introduces none of them --
the physical state is the only place an unresolved shortfall is ever recorded.
Finding F-7 records why the earlier one-threshold rule was withdrawn.

**Computational.**

9. the per-plan size cap does not bind: `max_plan_size >= |usable routes|`;
10. the complete finite plan space fits the declared exhaustive budget.

Condition 9 makes the cap incapable of deciding anything, which is what
`DEMAND_DRIVEN_PLAN_CAP_DISPOSITION.md` classifies it as. Condition 10 is what
makes `SEARCH_UNRESOLVED` impossible rather than merely unobserved, which is
the standing requirement for preregistration readiness.

## What Study 1 does not claim

`STUDY-1 DOMAIN VERIFIED` is **not** `GENERAL DEMAND-DRIVEN FRAMEWORK PROVED
FOR ALL LOSS/CAPACITY/TOPOLOGY MODELS`. Two known coupling artifacts live
outside the boundary and are kept as permanent regressions rather than
forgotten -- a non-binding declared storage capacity changes coupling, and two
lossy routes sharing one sink couple through it. Both are recorded in
`DEMAND_DRIVEN_MODEL_FINDINGS.md` as F-5 and F-6, and both worlds are refused
by `require_domain`.

## Registered failure semantics

`SEARCH_UNRESOLVED` inside a registered Study-1 job is a **computational
integrity failure**, not a physical result and not a data point. The whole job
is invalid. The trajectory does not continue, the epoch is not excluded, the
draw is not resampled, the seed is not changed. The implementation is
corrected and the identical job is rerun. `JobInvalid` is what enforces that:
it stops the run where the failure happened and names the coordinates needed
to repeat it exactly.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from gaussian_harness.numerics import Refusal, Vector

from .enumeration import EXHAUSTIVE_BUDGET, live_routes, usable_routes
from .world import ROLE_STOCK, DemandWorld

STUDY_ONE_DOMAIN_ID = "EBU-DEMAND-DRIVEN-STUDY-1-DOMAIN-v1"

# "partial economic service" is the precise entry: partial *physical*
# restoration is now supported and is the declared P-demand semantics (F-7).
FUTURE_UNSUPPORTED_PHYSICS = (
    "more than one resource",
    "lossy transfer",
    "loss sink",
    "irreversible sink",
    "recoverable waste",
    "upper destination-storage capacity",
    "topology change during a run",
    "partial economic service",
    "economic backlog quantity",
    "deadline",
    "service quality",
)


class JobInvalid(Refusal):
    """A registered Study-1 job that cannot be completed with integrity.

    Raised when the exact search failed to decide a question the registered
    design requires to be decided. It is not an outcome: the job produced no
    valid data, and the correct response is to fix the implementation and
    rerun the identical job with the identical seeds.
    """


def plan_space(world: DemandWorld) -> int:
    """`prod_r (1 + n_r) - 1` over usable routes: the complete plan space.

    A plan is a set of actions using each route at most once, so it is a
    choice, per usable route, of one of that route's `n_r` permitted quanta or
    of nothing, minus the empty plan. Unusable routes contribute a factor of
    one and are omitted. This is the exact size of the space an exhaustive
    Study-1 search would walk, and it is what condition 10 bounds.
    """
    total = 1
    for route in usable_routes(world):
        total *= 1 + sum(1 for quantum in world.quanta if quantum <= route.capacity)
        if total > 1 << 62:
            return total
    return total - 1


def action_bound(world: DemandWorld, state: Vector) -> int:
    """The largest number of actions any executable plan can hold here.

    One action per route, and only a live route can carry one, so the number
    of live routes bounds every plan at this baseline.
    """
    return len(live_routes(world, state))


def domain_violations(world: DemandWorld) -> tuple[str, ...]:
    """Every reason this world falls outside the frozen Study-1 domain."""
    found: list[str] = []
    resources = world.resources
    if len(resources) != 1:
        found.append(
            f"{len(resources)} resources {resources}; Study 1 supports one "
            "homogeneous scalar resource"
        )
    for index, coordinate in enumerate(world.coordinates):
        if coordinate.role != ROLE_STOCK:
            found.append(
                f"coordinate {index} ({coordinate.key}) is a {coordinate.role}; "
                "Study 1 declares no irreversible sinks"
            )
            continue
        if coordinate.capacity is not None:
            found.append(
                f"coordinate {index} ({coordinate.key}) declares an upper storage "
                f"capacity {coordinate.capacity}; Study 1 declares none"
            )
        if not coordinate.carries_potential:
            found.append(
                f"coordinate {index} ({coordinate.key}) declares no reference and "
                "scale; every Study-1 stock is valued"
            )
    for route in world.routes:
        if route.efficiency != 1:
            found.append(
                f"{route.route_id} has efficiency {route.efficiency}; Study 1 is "
                "lossless"
            )
        if route.sink is not None:
            found.append(f"{route.route_id} declares a loss sink; Study 1 has none")
    usable = usable_routes(world)
    if world.max_plan_size < len(usable):
        found.append(
            f"the plan-size cap {world.max_plan_size} binds against {len(usable)} "
            "usable routes; a Study-1 cap must be incapable of deciding anything"
        )
    space = plan_space(world)
    if space > EXHAUSTIVE_BUDGET:
        found.append(
            f"the complete plan space is {space}, above the exhaustive budget "
            f"{EXHAUSTIVE_BUDGET}; SEARCH_UNRESOLVED would not be impossible"
        )
    return tuple(found)


def in_domain(world: DemandWorld) -> bool:
    return not domain_violations(world)


def require_domain(world: DemandWorld) -> None:
    """Refuse a world that is outside the frozen Study-1 domain."""
    violations = domain_violations(world)
    if violations:
        raise Refusal(
            f"{world.world_id} is outside {STUDY_ONE_DOMAIN_ID}: "
            + "; ".join(violations)
        )


def state_violations(world: DemandWorld, state: Vector, total: Fraction | None = None):
    """Nonnegativity, and conservation against a declared total if given."""
    found: list[str] = []
    if len(state) != world.dimension:
        raise Refusal("state dimension does not match the world")
    for index, value in enumerate(state):
        if value < 0:
            found.append(f"coordinate {index} ({world.coordinates[index].key}) is {value}")
    if total is not None:
        for resource in world.resources:
            present = world.resource_total(state, resource)
            if present != total:
                found.append(f"{resource} totals {present}, not the declared {total}")
    return tuple(found)


@dataclass(frozen=True)
class CompletenessBound:
    """The finite Study-1 search argument, computed rather than asserted."""

    world_id: str
    coordinates: int
    usable_routes: int
    quanta: int
    atomic_actions: int
    plan_space: int
    exhaustive_budget: int
    plan_cap: int
    cap_binds: bool

    @property
    def unresolved_impossible(self) -> bool:
        """Whether `SEARCH_UNRESOLVED` is impossible for this world.

        The uncapped search evaluates at most one group per point of the plan
        space -- fewer, since it searches only the live structural reach --
        and returns `UNRESOLVED` only when the budget is exhausted first. If
        the whole space fits inside the budget, the budget can never be
        reached before the space is exhausted, so the verdict is always
        `SERVICEABLE` or `IMPOSSIBLE`.
        """
        return self.plan_space <= self.exhaustive_budget


def completeness_bound(world: DemandWorld) -> CompletenessBound:
    usable = usable_routes(world)
    actions = sum(
        sum(1 for quantum in world.quanta if quantum <= route.capacity)
        for route in usable
    )
    return CompletenessBound(
        world.world_id,
        world.dimension,
        len(usable),
        len(world.quanta),
        actions,
        plan_space(world),
        EXHAUSTIVE_BUDGET,
        world.max_plan_size,
        world.max_plan_size < len(usable),
    )
