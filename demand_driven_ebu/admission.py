"""Random compatible-subset admission of economic demand.

Admission is an upstream *economic* policy and it is not EBU. It may look at
exactly one thing: whether the obligations it would create are physically
serviceable. It is given no access to EBU values, to the potential, to capacity
balances or to future receipts, and it optimizes nothing -- not quantity, not
customer count, not value, not price, not age. Among the inclusion-maximal
subsets of arrivals it could admit, it picks one uniformly with its own
independent random stream.

That deliberate arbitrariness is the design. The purpose is to let a
demand-driven economy be studied without smuggling in a price system, a utility
function, a social priority order or a scheduler, any of which would confound
what the EBU mechanism itself contributes. A later study may replace this
policy; the mechanism must not depend on which one is in force.

A subset `S` is admissible when two conditions hold, both computed only from
physics:

* every arrival in `S` is itself serviceable once admitted, and
* admitting `S` newly breaks no pre-existing obligation.

The second condition is contract section 6. Physical demand cannot be rejected,
because it is literally encoded by the physical state, so a new *optional*
economic obligation must not be allowed to make an already-existing physical
need impossible to meet when that can be seen in advance. This is model
semantics and not a claim that physical need outranks economic need morally.
Pre-existing obligations that are *already* unserviceable are excluded from the
comparison rather than treated as vetoes; otherwise one stuck demand would
freeze admission permanently.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from gaussian_harness.numerics import Refusal, Vector

from .coupling import components
from .demand import (
    E_ADMITTED_PENDING,
    E_REJECTED_INCOMPATIBLE,
    E_REJECTED_PHYSICAL_SCARCITY,
    ActiveDemandSet,
    EconomicDemand,
    PhysicalDemand,
)
from .enumeration import SERVICEABLE, physically_serviceable
from .rng import STREAM_ADMISSION, Counter, uniform_index
from .world import DemandWorld

EVENT_ADMISSION = 1


@dataclass(frozen=True)
class AdmissionDecision:
    """A complete, replayable record of one admission event."""

    epoch: int
    incoming: tuple[str, ...]
    maximal_subsets: tuple[tuple[str, ...], ...]
    chosen_index: int
    rng_provenance: str
    admitted: tuple[str, ...]
    rejected: tuple[tuple[str, str], ...]

    @property
    def rejected_map(self) -> dict[str, str]:
        return dict(self.rejected)


def unserviceable_ids(
    world: DemandWorld,
    state: Vector,
    physical: tuple[PhysicalDemand, ...],
    economic: tuple[EconomicDemand, ...],
) -> frozenset[str]:
    """Demand ids whose component admits no complete executable plan now."""
    active = ActiveDemandSet.of(physical, economic)
    if active.is_empty:
        return frozenset()
    blocked: set[str] = set()
    for component in components(world, state, active):
        # Physical serviceability, decided without the plan-size cap. The cap
        # is an enumeration limit, so admission -- which asks a question about
        # physics -- must not consult it. A component serviceable only beyond
        # the cap is admitted and then reported SEARCH_INCOMPLETE, which makes
        # the limitation visible instead of encoding it as impossibility.
        if physically_serviceable(world, state, component.requirements) != SERVICEABLE:
            blocked.update(component.demand_ids)
    return frozenset(blocked)


def admissible(
    world: DemandWorld,
    state: Vector,
    physical: tuple[PhysicalDemand, ...],
    held: tuple[EconomicDemand, ...],
    baseline_blocked: frozenset[str],
    subset: tuple[EconomicDemand, ...],
) -> bool:
    blocked = unserviceable_ids(world, state, physical, tuple(held) + tuple(subset))
    if any(demand.demand_id in blocked for demand in subset):
        return False
    pre_existing = {demand.demand_id for demand in physical} | {
        demand.demand_id for demand in held
    }
    newly_broken = (blocked & pre_existing) - baseline_blocked
    return not newly_broken


def admit(
    world: DemandWorld,
    state: Vector,
    physical: tuple[PhysicalDemand, ...],
    held: tuple[EconomicDemand, ...],
    incoming: tuple[EconomicDemand, ...],
    seed: int,
    epoch: int,
) -> tuple[tuple[EconomicDemand, ...], tuple[EconomicDemand, ...], AdmissionDecision]:
    """Admit one uniformly chosen inclusion-maximal compatible subset."""
    ordered = tuple(sorted(incoming, key=lambda demand: demand.demand_id))
    baseline_blocked = unserviceable_ids(world, state, physical, held)

    feasible_subsets: list[tuple[EconomicDemand, ...]] = []
    for size in range(len(ordered) + 1):
        for chosen in combinations(ordered, size):
            if admissible(world, state, physical, held, baseline_blocked, chosen):
                feasible_subsets.append(chosen)
    if not feasible_subsets:
        raise Refusal("the empty subset must always be admissible")

    as_sets = [frozenset(demand.demand_id for demand in subset) for subset in feasible_subsets]
    maximal = [
        subset
        for subset, ids in zip(feasible_subsets, as_sets)
        if not any(ids < other for other in as_sets)
    ]
    maximal.sort(key=lambda subset: tuple(demand.demand_id for demand in subset))

    counter = Counter(
        "EBU-DEMAND-DRIVEN-ECONOMY-v1",
        world.world_id,
        seed,
        STREAM_ADMISSION,
        epoch,
        EVENT_ADMISSION,
        0,
    )
    index, _ = uniform_index(counter, len(maximal))
    selection = maximal[index]
    selected_ids = {demand.demand_id for demand in selection}

    admitted = tuple(
        demand.with_status(E_ADMITTED_PENDING)
        for demand in ordered
        if demand.demand_id in selected_ids
    )
    rejected: list[EconomicDemand] = []
    reasons: list[tuple[str, str]] = []
    for demand in ordered:
        if demand.demand_id in selected_ids:
            continue
        alone = admissible(world, state, physical, held, baseline_blocked, (demand,))
        reason = E_REJECTED_INCOMPATIBLE if alone else E_REJECTED_PHYSICAL_SCARCITY
        rejected.append(demand.with_status(reason))
        reasons.append((demand.demand_id, reason))

    decision = AdmissionDecision(
        epoch,
        tuple(demand.demand_id for demand in ordered),
        tuple(tuple(demand.demand_id for demand in subset) for subset in maximal),
        index,
        counter.provenance,
        tuple(demand.demand_id for demand in admitted),
        tuple(reasons),
    )
    return admitted, tuple(rejected), decision
