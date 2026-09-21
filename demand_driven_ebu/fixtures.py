"""Small exact worlds for hand-checkable conformance.

Every world here is tiny, integer-referenced and exactly rational, so each
fixture result can be recomputed by hand from the declared numbers. None of
them is a scientific configuration and none is tuned toward a favourable
outcome: several exist precisely to exhibit refusal, scarcity, unaffordability
and irreversible loss.

The sand/water world deliberately puts the two resources on disjoint nodes.
Because accounts are held by nodes, sharing a node would couple the two
resources through joint affordability, and the independence fixture would then
be testing nothing. Independence has to be built, not assumed.
"""

from __future__ import annotations

from fractions import Fraction as F

from .arrivals import ArrivalProcess
from .capacity import CapacityLedger
from .disturbance import DisturbanceProcess
from .world import Coordinate, DemandWorld, Route


def _complete_routes(resource: str, indices, capacity) -> list[Route]:
    return [
        Route.declare(resource, source, destination, capacity)
        for source in indices
        for destination in indices
        if source != destination
    ]


def sandwater_world(max_plan_size: int = 2) -> DemandWorld:
    """Sand on nodes A, B, C and water on nodes D, E; the two never interact.

    Indices: sand|A 0, sand|B 1, sand|C 2, water|D 3, water|E 4.
    """
    coordinates = [
        Coordinate.stock("sand", "A", 10, 1),
        Coordinate.stock("sand", "B", 10, 1),
        Coordinate.stock("sand", "C", 10, 1),
        Coordinate.stock("water", "D", 6, 1),
        Coordinate.stock("water", "E", 6, 1),
    ]
    routes = _complete_routes("sand", (0, 1, 2), 30) + _complete_routes("water", (3, 4), 20)
    return DemandWorld.declare("sandwater-v1", coordinates, routes, (1, 2, 3), max_plan_size)


def surplus_world() -> DemandWorld:
    """A world holding more than its reference, so a delivery can be restorative.

    With references (8, 8, 8) and 30 units present there is no shortfall
    anywhere, hence no physical demand, yet the state is far from the
    reference. An economic delivery that drains the surplus therefore earns
    EBU: economic demand and physical need are genuinely distinct here.
    """
    coordinates = [
        Coordinate.stock("sand", "A", 8, 1),
        Coordinate.stock("sand", "B", 8, 1),
        Coordinate.stock("sand", "C", 8, 1),
    ]
    return DemandWorld.declare(
        "surplus-v1", coordinates, _complete_routes("sand", (0, 1, 2), 30), (1, 2, 3), 2
    )


def scarcity_world() -> DemandWorld:
    """560 units exist; the alphabet can ask for 1000."""
    coordinates = [
        Coordinate.stock("sand", "A", 560, 1),
        Coordinate.stock("sand", "B", 0, 1),
        Coordinate.stock("sand", "C", 0, 1),
    ]
    return DemandWorld.declare(
        "scarcity-v1", coordinates, _complete_routes("sand", (0, 1, 2), 1000), (560, 1000), 2
    )


def competing_world() -> DemandWorld:
    """Three units at A; two destinations each wanting all three."""
    coordinates = [
        Coordinate.stock("sand", "A", 3, 1),
        Coordinate.stock("sand", "B", 0, 1),
        Coordinate.stock("sand", "C", 0, 1),
    ]
    routes = [
        Route.declare("sand", 0, 1, 3),
        Route.declare("sand", 0, 2, 3),
    ]
    return DemandWorld.declare("competing-v1", coordinates, routes, (3,), 2)


def cycle_world() -> DemandWorld:
    """Four unit-scale cells, used for the exact circulation fixture.

    The scales and quanta are chosen so that the worked sequence lands on
    E = -20, +8, +7, +5 exactly, and the state returns exactly.
    """
    coordinates = [
        Coordinate.stock("sand", "A", 10, 1),
        Coordinate.stock("sand", "B", 10, 1),
        Coordinate.stock("sand", "C", 10, 1),
        Coordinate.stock("sand", "D", 10, 1),
    ]
    return DemandWorld.declare(
        "cycle-v1", coordinates, _complete_routes("sand", (0, 1, 2, 3), 30), (1, 2, 3, 4), 3
    )


def loss_world() -> DemandWorld:
    """Three cells plus a loss sink that is inside V.

    The route A -> B wastes half of what it carries into `sand|W`. Because the
    sink carries potential, the waste is a real and permanent deviation rather
    than a bookkeeping entry, and no route leads out of it.

    Indices: sand|A 0, sand|B 1, sand|C 2, sand|W 3.
    """
    coordinates = [
        Coordinate.stock("sand", "A", 10, 1),
        Coordinate.stock("sand", "B", 10, 1),
        Coordinate.stock("sand", "C", 10, 1),
        Coordinate.sink_in_potential("sand", "W", 0, 1),
    ]
    routes = [
        Route.declare("sand", 0, 1, 4, F(1, 2), 3),
        Route.declare("sand", 1, 0, 4),
        Route.declare("sand", 1, 2, 4),
        Route.declare("sand", 2, 1, 4),
    ]
    return DemandWorld.declare("loss-v1", coordinates, routes, (1, 2, 3, 4), 2)


def audit_sink_world() -> DemandWorld:
    """The same shape, but the sink is outside V and purely an audit ledger.

    Nothing may pretend this sink generates a homeostatic demand: it has no
    reference to fall below. It exists so that conservation closes.
    """
    coordinates = [
        Coordinate.stock("sand", "A", 10, 1),
        Coordinate.stock("sand", "B", 10, 1),
        Coordinate.sink_audit_only("sand", "W"),
    ]
    routes = [
        Route.declare("sand", 0, 1, 4, F(1, 2), 2),
        Route.declare("sand", 1, 0, 4),
    ]
    return DemandWorld.declare("audit-sink-v1", coordinates, routes, (1, 2, 3, 4), 2)


def seeded_ledger(world: DemandWorld, amount) -> CapacityLedger:
    """A hand-worked accounting fixture's opening balances.

    This is not the model's bootstrap. Contract section 29 starts every run at
    `B_i = 0` and the harness enforces that; section 28's circulation example
    is explicitly a worked accounting illustration and declares its own opening
    total, which is why seeding is available here and nowhere else.
    """
    return CapacityLedger(tuple((node, F(amount)) for node in world.nodes))


def quiet_disturbance(world: DemandWorld) -> DisturbanceProcess:
    """A declared disturbance that never fires. For fixtures with no weather."""
    pairs = ((0, 1),)
    return DisturbanceProcess.declare(world, pairs, 1, 0, 1)


def no_arrivals() -> ArrivalProcess:
    return ArrivalProcess.declare((("sand", "A", 1),), 0, 1, 0)


class ScriptedArrivals:
    """A deterministic arrival schedule, for hand-worked fixtures only.

    It satisfies the same interface as `ArrivalProcess` and is a degenerate
    instance of the same object: a law that is a function of the epoch alone.
    Being deterministic it is trivially blind to EBU, capacity and policy,
    which is exactly what a hand-checkable fixture needs. No study may use it;
    the registered arrival law is a declared stochastic process whose
    parameters are still unresolved.
    """

    def __init__(self, script: dict[int, tuple[tuple[str, str, object], ...]]):
        self.script = dict(script)

    def arrivals(self, world: DemandWorld, seed: int, epoch: int):
        from .demand import EconomicDemand

        return tuple(
            EconomicDemand.declare(world, resource, quantity, node, epoch, index)
            for index, (resource, node, quantity) in enumerate(self.script.get(epoch, ()))
        )


class ScriptedDisturbance:
    """A deterministic external-disturbance schedule, for hand-worked fixtures.

    Same interface as `DisturbanceProcess`, and like `ScriptedArrivals` it is a
    degenerate instance of the same object: a law that is a function of the
    epoch alone. It exists so that cycle-provenance fixtures can place external
    physical events at exact epochs, including events that cancel in the
    potential or permute stock at constant `V`.
    """

    def __init__(self, script: dict[int, tuple[int, int, object]]):
        self.script = dict(script)

    def draw(self, world: DemandWorld, state, seed: int, epoch: int):
        from .disturbance import (
            STATUS_APPLIED,
            STATUS_NOT_SCHEDULED,
            STATUS_NULL_UNAVAILABLE,
            DisturbanceEvent,
        )

        entry = self.script.get(epoch)
        if entry is None:
            return DisturbanceEvent(STATUS_NOT_SCHEDULED, None, None, F(0))
        source, destination, quantity = entry
        amount = F(quantity)
        if state[source] < amount:
            return DisturbanceEvent(STATUS_NULL_UNAVAILABLE, source, destination, F(0))
        return DisturbanceEvent(STATUS_APPLIED, source, destination, amount)


def routeless_world() -> DemandWorld:
    """Two stocks of one resource and no routes at all.

    Nothing can ever be served here, so the actor never acts and an external
    disturbance is the only thing that moves the state. That makes it the exact
    setting for cycle-provenance fixtures: a pair of external events can be
    made to cancel in the potential and return the state, with no actor
    activity confounding the window.
    """
    coordinates = [
        Coordinate.stock("sand", "A", 10, 1),
        Coordinate.stock("sand", "B", 10, 1),
    ]
    return DemandWorld.declare("routeless-v1", coordinates, (), (1, 2), 1)


def triple_delivery_world(
    unusable: bool = False,
    binding_shared_route: bool = False,
    irrelevant_route: bool = False,
    max_plan_size: int = 2,
) -> DemandWorld:
    """The independent auditor's counterexample world, and its variants.

    Three independent one-unit deliveries `A -> B`, `C -> D`, `E -> F`. Each
    source holds exactly one usable unit, each destination is one unit short,
    and each delivery has a distinct owner, so nothing genuinely couples.

    `unusable` adds two connecting routes of capacity `1/2` while the only
    permitted action quantity is `1`. They can carry no action, so the
    executable action set is unchanged and they must be behaviorally
    invisible. Under the superseded coupling rule they merged all three
    demands and, with a plan cap of two against three required actions,
    destroyed every service plan.

    `binding_shared_route` adds a usable `A -> D`, which makes `A` a possible
    supplier for two demands that hold one unit between them: a genuine
    competition for scarce stock, so coupling there is correct.

    `irrelevant_route` adds a usable route between two coordinates carrying no
    demand. It is executable and serves nothing, and must create no coupling.
    """
    names = (("A", 0), ("B", 1), ("C", 0), ("D", 1), ("E", 0), ("F", 1))
    coordinates = [Coordinate.stock("r", node, reference, 1) for node, reference in names]
    routes = [
        Route.declare("r", 0, 1, 1),
        Route.declare("r", 2, 3, 1),
        Route.declare("r", 4, 5, 1),
    ]
    if unusable:
        routes += [Route.declare("r", 1, 2, F(1, 2)), Route.declare("r", 3, 4, F(1, 2))]
    if binding_shared_route:
        routes += [Route.declare("r", 0, 3, 1)]
    if irrelevant_route:
        coordinates += [
            Coordinate.stock("r", "G", 0, 1),
            Coordinate.stock("r", "H", 0, 1),
        ]
        routes += [Route.declare("r", 6, 7, 1)]
    return DemandWorld.declare("triple-delivery-v1", coordinates, routes, (1,), max_plan_size)


def triple_delivery_state(world: DemandWorld):
    """One unit at each odd-indexed source, nothing at the destinations."""
    return tuple(
        F(1) if coordinate.reference == 0 else F(0)
        for coordinate in world.coordinates
    )


def shared_source_world() -> DemandWorld:
    """Two destinations supplied only from one coordinate holding one unit."""
    coordinates = [
        Coordinate.stock("r", "A", 0, 1),
        Coordinate.stock("r", "B", 1, 1),
        Coordinate.stock("r", "D", 1, 1),
    ]
    routes = [Route.declare("r", 0, 1, 1), Route.declare("r", 0, 2, 1)]
    return DemandWorld.declare("shared-source-v1", coordinates, routes, (1,), 2)


def wide_supply_world(sources: int = 19, requirement: int = 1) -> DemandWorld:
    """Many independent one-unit suppliers feeding one destination.

    The second auditor's uncertainty counterexample. With nineteen suppliers
    the per-route search space is `2^19`, which a worst-case pre-check refuses
    outright -- yet nineteen one-action plans serve the destination and the
    menu is not empty. Raising `requirement` above the number of suppliers
    makes the requirement genuinely unsatisfiable while keeping the space
    large, which is what forces a real `SEARCH_BUDGET_EXCEEDED`.
    """
    coordinates = [
        Coordinate.stock("r", f"S{index:02d}", 0, 1) for index in range(sources)
    ]
    coordinates.append(Coordinate.stock("r", "T", requirement, 1))
    destination = len(coordinates) - 1
    routes = [Route.declare("r", index, destination, 1) for index in range(sources)]
    return DemandWorld.declare("wide-supply-v1", coordinates, routes, (1,), 2)


def wide_supply_state(world: DemandWorld):
    """One unit at every supplier, nothing at the destination."""
    return tuple(
        F(0) if coordinate.node == "T" else F(1) for coordinate in world.coordinates
    )


def empty_source_world(extra: bool = False) -> DemandWorld:
    """The three deliveries, optionally plus routes whose sources are empty.

    The added routes `B -> D` and `D -> F` have capacity one and can carry the
    only permitted quantum, so a capacity-only usability test calls them
    usable. But `B` and `D` hold nothing at this state, and source-funding
    forbids a coordinate paying for an outflow with quantity arriving in the
    same instant -- so neither route can carry an action in any plan here, not
    even inside a simultaneous group. The executable action set is unchanged
    and they must be behaviorally invisible.
    """
    coordinates = [
        Coordinate.stock("r", node, reference, 1)
        for node, reference in (("A", 0), ("B", 1), ("C", 0), ("D", 1), ("E", 0), ("F", 1))
    ]
    routes = [
        Route.declare("r", 0, 1, 1),
        Route.declare("r", 2, 3, 1),
        Route.declare("r", 4, 5, 1),
    ]
    if extra:
        routes += [Route.declare("r", 1, 3, 1), Route.declare("r", 3, 5, 1)]
    return DemandWorld.declare("empty-source-v1", coordinates, routes, (1,), 2)


def study_one_world() -> DemandWorld:
    """The frozen Study-1 shape: one resource, lossless, no storage capacity.

    Three stocks in a line, `A <-> B <-> C`, two declared quanta and a
    plan-size cap equal to the number of usable routes, so the cap cannot
    decide anything. The complete plan space is `3^4 - 1 = 80`, far inside the
    exhaustive budget, which is what makes `SEARCH_UNRESOLVED` impossible here
    rather than merely unobserved. See `study_one.completeness_bound`.

    Indices: r|A 0, r|B 1, r|C 2. Total resource 12, references (4, 4, 4).
    """
    coordinates = [Coordinate.stock("r", node, 4, 1) for node in ("A", "B", "C")]
    routes = [
        Route.declare("r", 0, 1, 6),
        Route.declare("r", 1, 0, 6),
        Route.declare("r", 1, 2, 6),
        Route.declare("r", 2, 1, 6),
    ]
    return DemandWorld.declare("study-one-v1", coordinates, routes, (1, 2), 4)


def study_one_state(*values):
    """A Study-1 state, defaulting to the reference (4, 4, 4)."""
    chosen = values if values else (4, 4, 4)
    return tuple(F(value) for value in chosen)


def capacity_relief_world(declare_capacity: bool = True) -> DemandWorld:
    """OUTSIDE STUDY-1 DOMAIN. A non-binding storage capacity changes coupling.

    Two unrelated one-unit deliveries: `A -> C` and `V -> W`. Nothing connects
    them, and with `declare_capacity=False` the model correctly reports two
    independent components.

    With `declare_capacity=True` the coordinate `C` declares an upper storage
    capacity of ten. Only three units of resource exist in the whole world, so
    the capacity can never bind, no executable action changes, and no genuine
    constraint changes. But the structural reach carries a *capacity-relief*
    limb -- a route out of a capacity-bearing requirement coordinate might be
    needed to make room -- so `C -> Z` enters the reach of the demand at `C`,
    drags `Z` in behind it, and then `V -> Z` drags in `V` and its owner. The
    two demands merge.

    This is a genuine tightness failure of the reach in the storage-capacity
    domain, and it is kept as a permanent regression rather than repaired:
    Study 1 declares no storage capacities, and `study_one.require_domain`
    refuses this world. Recorded as finding F-5.

    Indices: r|A 0, r|C 1, r|V 2, r|W 3, r|Z 4.
    """
    coordinates = [
        Coordinate.stock("r", "A", 1, 1),
        Coordinate.stock("r", "C", 1, 1, 10 if declare_capacity else None),
        Coordinate.stock("r", "V", 1, 1),
        Coordinate.stock("r", "W", 0, 1),
        Coordinate.stock("r", "Z", 0, 1),
    ]
    routes = [
        Route.declare("r", 0, 1, 1),
        Route.declare("r", 1, 4, 1),
        Route.declare("r", 2, 3, 1),
        Route.declare("r", 2, 4, 1),
    ]
    return DemandWorld.declare("capacity-relief-v1", coordinates, routes, (1,), 4)


def capacity_relief_state():
    """One unit each at `A`, `C` and `V`; nothing at `W` or `Z`."""
    return (F(1), F(1), F(1), F(0), F(0))


def shared_sink_world(lossy: bool = True) -> DemandWorld:
    """OUTSIDE STUDY-1 DOMAIN. Two lossy routes couple through their sink.

    Two unrelated deliveries, `A -> C` and `B -> D`. With `lossy=False` they
    are independent, as they should be.

    With `lossy=True` both routes waste half of what they carry into the same
    audit sink `S`. The sink enters the reach of each demand as a delivery
    target, and then every route depositing into that sink is pulled in behind
    it -- so the demand at `C` acquires `B`, `D` and owner `B`, and the two
    merge. A sink is irreversible, carries no capacity and may not be the
    source of any route, so it cannot compete for anything: the coupling is
    spurious.

    Kept as a permanent regression, not repaired. Study 1 is lossless and
    declares no sinks, and `study_one.require_domain` refuses this world.
    Recorded as finding F-6.

    Indices: r|A 0, r|B 1, r|C 2, r|D 3, r|S 4.
    """
    coordinates = [
        Coordinate.stock("r", "A", 2, 1),
        Coordinate.stock("r", "B", 2, 1),
        Coordinate.stock("r", "C", 0, 1),
        Coordinate.stock("r", "D", 0, 1),
        Coordinate.sink_audit_only("r", "S"),
    ]
    if lossy:
        routes = [
            Route.declare("r", 0, 2, 2, F(1, 2), 4),
            Route.declare("r", 1, 3, 2, F(1, 2), 4),
        ]
    else:
        routes = [Route.declare("r", 0, 2, 2), Route.declare("r", 1, 3, 2)]
    return DemandWorld.declare("shared-sink-v1", coordinates, routes, (2,), 2)


def shared_sink_state():
    """Two units each at `A` and `B`; nothing anywhere else."""
    return (F(2), F(2), F(0), F(0), F(0))


def two_supplier_world() -> DemandWorld:
    """Two suppliers, two destinations, every supplier able to serve either.

    The auditor's accepted-domain sampling fixture. With one unit needed at
    each destination there are **four** distinct irredundant plan identities

        {A->C, A->D}   {A->C, B->D}   {B->C, A->D}   {B->C, B->D}

    but only **three** distinct modeled outcomes: the two cross plans move one
    unit out of each supplier and are indistinguishable in increment, in
    post-state and in owner receipts, because `C` and `D` are identical in
    reference, scale and stock and the swap `C <-> D` is an automorphism.

    So the outcome map is genuinely many-to-one here, and uniform sampling
    over plan identities induces `1/4, 1/2, 1/4` over outcomes -- **not**
    `1/3` each. This world exists to pin that down.

    Indices: r|A 0, r|B 1, r|C 2, r|D 3.
    """
    coordinates = [
        Coordinate.stock("r", node, reference, 1)
        for node, reference in (("A", 2), ("B", 2), ("C", 0), ("D", 0))
    ]
    routes = [
        Route.declare("r", 0, 2, 2),
        Route.declare("r", 0, 3, 2),
        Route.declare("r", 1, 2, 2),
        Route.declare("r", 1, 3, 2),
    ]
    return DemandWorld.declare("two-supplier-v1", coordinates, routes, (1,), 4)


def two_supplier_state():
    """Two units at each supplier, nothing at either destination."""
    return (F(2), F(2), F(0), F(0))


def blocked_neighbour_state():
    """`study_one_world` at (0, 6, 6): a blocked demand beside a live one.

    The auditor's independent-progress counterexample. At this state the
    physical demand at `A` is four units short and the only route into `A`
    carries at most two, so it is **proved impossible**. An economic order of
    one unit at `C` is independent of it and has exactly two complete plans,
    `B->C` at one unit and at two.

    The runtime serves `C` and leaves `A` unresolved. An oracle that asks
    "is there one plan serving every active demand?" answers *no*, returns the
    empty set, and agrees vacuously with a component path that also returns
    empty -- which is why that oracle could not see this.
    """
    return study_one_state(0, 6, 6)
