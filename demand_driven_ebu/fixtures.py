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
