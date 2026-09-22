"""The demand-driven epoch: disturbance, arrival, admission, service, settlement.

One epoch runs exactly this sequence, and the order is the scientific content
of the correction rather than an implementation convenience:

     1 natural disturbance            x_t -> y_t, external deviation recorded
     2 derive P-demand from y_t       read off the state, never remembered
     3 economic arrivals              pure function of (seed, epoch)
     4 random compatible admission    EBU-blind, physics-only
     5 active demand set D_t          unordered union of P and admitted E
     6 demand-dependency components    coupled sets, resolved jointly
     7 complete service plans          per component
     8 can this plan actually happen?  physical executability
     9 exact EBU valuation             only now does a value exist
    10 affordability                   capacity decides only this
    11 actor choice                    among equally complete answers
    12 joint closure gate              independent components combined once
    13 execution                       y_t + delta_G -> x_{t+1}
    14 capacity settlement             common-path receipts of the combined group
    15 P-demand re-derivation          cached representation discarded
    16 audit                           exact residuals, tolerance zero

Steps 1-4 cannot see EBU. Step 9 cannot see capacity. Step 10 cannot change
what step 9 measured. Nothing anywhere sorts demands, and no step consults how
long a demand has been waiting.

Independent components execute in the same epoch. They are combined into one
group and valued once, and the gate at step 12 checks that combining them
changed nothing: the group's EBU must equal the sum of the component EBUs and
every receipt must be unchanged. A discrepancy means two supposedly independent
components in fact interact, which is a defect in the dependency graph. The
harness refuses loudly rather than quietly sequencing them, because quiet
sequencing would hide the defect and invent a service order this model does not
have.

## Registered Study-1 mode

`registered=True` refuses to start outside the frozen Study-1 domain
(`study_one`) and turns every undecided search into `JobInvalid`. That is the
declared failure semantics: `SEARCH_UNRESOLVED` inside a registered job is a
computational integrity failure, the whole job is invalid, and the correct
response is to fix the implementation and rerun the identical job -- never to
continue, exclude the epoch, resample, or change the seed. Inside the frozen
domain the failure is impossible by construction, so `JobInvalid` should be
unreachable; it exists to make sure that if the construction is ever wrong,
the run stops instead of quietly recording a computational limit as physics.

`decomposition_gate=True` additionally verifies, every epoch, that the
component decomposition reproduces the decomposition-free
**policy-conditioned** reference exactly: the physical plan set, the
affordable set under this run's balances, the selection law this policy
induces over canonical plan identities, and the modeled-outcome law it pushes
forward. That reference, not the decomposition, is the scientific authority.
It lets an independent part progress while another is proved blocked or is
EBU-unaffordable, which is what the runtime does, and it is conditioned on
the arm's own balances, because an EBU arm never chooses from the
pre-affordability set.

This module advances model state. Running it is a transition, not a result.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

from gaussian_harness.numerics import Refusal, Vector, add, exact

from .admission import AdmissionDecision, admit, unresolved_ids
from .arrivals import ArrivalProcess
from .capacity import CapacityLedger
from .coupling import DemandComponent, components
from .demand import (
    LIFECYCLE_ADMITTED,
    LIFECYCLE_ADMITTED_BUT_EBU_UNAFFORDABLE,
    LIFECYCLE_ADMITTED_BUT_UNRESOLVED_PHYSICAL,
    LIFECYCLE_ARRIVED,
    LIFECYCLE_REJECTED_INCOMPATIBLE,
    LIFECYCLE_REJECTED_PHYSICAL_SCARCITY,
    LIFECYCLE_SERVED,
    ActiveDemandSet,
    EconomicDemand,
    derive_physical_demands,
    state_identity,
)
from .service import requirements, served_economic_ids
from .disturbance import DisturbanceProcess, apply_disturbance
from .physical import PlanGroup, can_happen_now
from .plans import ServicePlan, enumerate_service_plans, serviceability
from .policies import POLICY_CONTROL, choose, specification
from .oracle import policy_levels
from .rng import STREAM_ACTOR, Counter
from .study_one import JobInvalid, action_bound, require_domain
from .valuation import value_group
from .world import DemandWorld

MODEL_ID = "EBU-DEMAND-DRIVEN-ECONOMY-v1"
EVENT_ACTOR = 2

STATUS_NO_ACTIVE_DEMAND = "NO_ACTIVE_DEMAND"
STATUS_NO_COMPLETE_PLAN = "NO_COMPLETE_PHYSICAL_PLAN"
STATUS_SEARCH_INCOMPLETE = "SEARCH_INCOMPLETE_AT_PLAN_CAP"
STATUS_SEARCH_UNRESOLVED = "SEARCH_BUDGET_EXCEEDED"
STATUS_ALL_UNAFFORDABLE = "ALL_PLANS_EBU_UNAFFORDABLE"
STATUS_EXECUTED = "EXECUTED"
DECLARED_STATUSES = (
    STATUS_NO_ACTIVE_DEMAND,
    STATUS_NO_COMPLETE_PLAN,
    STATUS_SEARCH_INCOMPLETE,
    STATUS_SEARCH_UNRESOLVED,
    STATUS_ALL_UNAFFORDABLE,
    STATUS_EXECUTED,
)

# An empty menu is reported as physical impossibility only when an uncapped
# search establishes it. The plan-size cap is an enumeration limit and may not
# decide physics on its own.
_EMPTY_MENU_STATUS = {
    "SERVICEABLE_WITHIN_CAP": STATUS_EXECUTED,
    "SEARCH_INCOMPLETE_AT_PLAN_CAP": STATUS_SEARCH_INCOMPLETE,
    "PHYSICALLY_IMPOSSIBLE": STATUS_NO_COMPLETE_PLAN,
    "SEARCH_BUDGET_EXCEEDED": STATUS_SEARCH_UNRESOLVED,
}

GATE_CLOSED = "JOINT_CLOSURE_VERIFIED"
GATE_DEFECT = "DEPENDENCY_GRAPH_INCOMPLETE"

DECOMPOSITION_NOT_CHECKED = "DECOMPOSITION_NOT_CHECKED"
DECOMPOSITION_VERIFIED = "POLICY_EXECUTION_EQUALS_GLOBAL_REFERENCE"
DECOMPOSITION_DEFECT = "POLICY_EXECUTION_DIFFERS_FROM_GLOBAL_REFERENCE"

_REJECTION_LIFECYCLE = {
    "E_REJECTED_PHYSICAL_SCARCITY": LIFECYCLE_REJECTED_PHYSICAL_SCARCITY,
    "E_REJECTED_INCOMPATIBLE": LIFECYCLE_REJECTED_INCOMPATIBLE,
}


@dataclass(frozen=True)
class ArrivalOutcome:
    """One incoming economic demand, tracked over the common raw arrival set.

    Arms share an exogenous arrival stream but reach different physical states,
    so they legitimately admit different subsets. A service rate over admitted
    demands alone is therefore not a whole-system measure: an arm that admits
    little and serves all of it would score perfectly. Every arrival gets a row
    here so comparisons can be reported over arrivals, which are identical
    across arms by construction.
    """

    demand_id: str
    resource: str
    quantity: Fraction
    destination: int
    arrival_epoch: int
    state: str
    resolved_epoch: int | None = None

    def at(self, state: str, epoch: int | None = None) -> "ArrivalOutcome":
        return ArrivalOutcome(
            self.demand_id,
            self.resource,
            self.quantity,
            self.destination,
            self.arrival_epoch,
            state,
            epoch if epoch is not None else self.resolved_epoch,
        )


def read_code_identity() -> str:
    """SHA-256 over the package sources, read fresh from disk every call.

    Use this to pin a run at its start and check it again at the end. A run
    whose code identity moved underneath it is not reproducible, and the
    difference must be reported rather than absorbed.
    """
    digest = hashlib.sha256()
    for path in sorted(Path(__file__).parent.glob("*.py")):
        digest.update(path.name.encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


@lru_cache(maxsize=1)
def code_identity() -> str:
    """The cached identity stamped on every record.

    Memoised because it is written once per epoch and re-hashing the package
    each time dominated the cost of short runs. `read_code_identity` remains
    available for the start/end pin, which is what would actually notice a
    change.
    """
    return read_code_identity()


@dataclass(frozen=True)
class ComponentOutcome:
    component_id: str
    demand_ids: tuple[str, ...]
    status: str
    plan_count: int
    affordable_count: int
    chosen_plan_id: str | None
    chosen_ebu: Fraction | None


@dataclass(frozen=True)
class EpochRecord:
    """One fully replayable epoch. Aggregates alone are never stored."""

    run_id: str
    code_id: str
    policy: str
    epoch: int
    state_before: Vector
    state_forced: Vector
    state_after: Vector
    disturbance_status: str
    external_events: tuple[str, ...]
    external_deviation: Fraction
    potential_before: Fraction
    potential_forced: Fraction
    potential_after: Fraction
    arrivals: tuple[str, ...]
    admission: AdmissionDecision | None
    admitted_now: tuple[str, ...]
    rejected_now: tuple[tuple[str, str], ...]
    active_physical: tuple[str, ...]
    active_economic: tuple[str, ...]
    outcomes: tuple[ComponentOutcome, ...]
    executed_group_id: str
    executed_provenance: tuple[tuple[str, tuple[str, ...]], ...]
    epoch_ebu: Fraction
    receipts: tuple[tuple[str, Fraction], ...]
    owner_deltas: tuple[tuple[str, Fraction], ...]
    balances: tuple[tuple[str, Fraction], ...]
    balance_total: Fraction
    served_economic: tuple[str, ...]
    unaffordable_economic: tuple[str, ...]
    unresolved_economic: tuple[str, ...]
    arrival_states: tuple[tuple[str, str], ...]
    joint_gate: str
    accounting_residual: Fraction
    conservation_residual: Fraction
    nonnegativity_residual: Fraction
    separability_residual: Fraction
    epoch_status: str
    decomposition_gate: str = DECOMPOSITION_NOT_CHECKED


@dataclass
class EconomyRun:
    """A stateful demand-driven economy. Advancing it is a model transition."""

    world: DemandWorld
    disturbance: DisturbanceProcess
    arrivals: ArrivalProcess
    policy: str
    natural_seed: int
    arrival_seed: int
    admission_seed: int
    actor_seed: int
    initial_state: Vector | None = None
    registered: bool = False
    decomposition_gate: bool = False

    state: Vector = field(init=False)
    ledger: CapacityLedger = field(init=False)
    held: tuple[EconomicDemand, ...] = field(init=False, default=())
    epoch: int = field(init=False, default=0)
    external_total: Fraction = field(init=False, default=Fraction(0))
    external_events: list[str] = field(init=False, default_factory=list)
    arrival_ledger: dict[str, ArrivalOutcome] = field(init=False, default_factory=dict)
    initial_potential: Fraction = field(init=False)
    records: list[EpochRecord] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        specification(self.policy)
        if self.registered:
            # A registered Study-1 job may not be started outside the frozen
            # domain. Everything the completeness argument rests on -- exact
            # exhaustive search, a non-binding plan cap, impossible
            # SEARCH_UNRESOLVED -- is a property of that domain and of
            # nothing wider. See `study_one`.
            require_domain(self.world)
        self.state = (
            self.world.reference_state() if self.initial_state is None else self.initial_state
        )
        if len(self.state) != self.world.dimension:
            raise Refusal("initial state dimension does not match the world")
        constrained = self.policy != POLICY_CONTROL
        self.ledger = CapacityLedger.zero(self.world.nodes, constrained=constrained)
        self.initial_potential = self.world.potential.value_total(self.state)

    @property
    def run_id(self) -> str:
        text = "|".join(
            (
                MODEL_ID,
                self.world.world_id,
                self.policy,
                str(self.natural_seed),
                str(self.arrival_seed),
                str(self.admission_seed),
                str(self.actor_seed),
                state_identity(self.state if not self.records else self.records[0].state_before),
            )
        )
        return hashlib.sha256(text.encode("ascii")).hexdigest()[:16]

    def _actor_counter(self, ordinal: int) -> Counter:
        return Counter(
            MODEL_ID,
            self.world.world_id,
            self.actor_seed,
            STREAM_ACTOR,
            self.epoch,
            EVENT_ACTOR,
            ordinal,
        )

    def _select(
        self, component: DemandComponent, plans: tuple[ServicePlan, ...], ordinal: int, forced: Vector
    ) -> tuple[ComponentOutcome, ServicePlan | None, Fraction | None]:
        if not plans:
            status = _EMPTY_MENU_STATUS[serviceability(self.world, forced, component)]
            if self.registered and status in (
                STATUS_SEARCH_UNRESOLVED,
                STATUS_SEARCH_INCOMPLETE,
            ):
                raise JobInvalid(
                    f"{status} at epoch {self.epoch} for {component.component_id} "
                    f"in registered job {self.run_id}. A registered Study-1 job "
                    "may not record a search failure as a result: the whole job "
                    "is invalid. Do not continue the trajectory, do not exclude "
                    "the epoch, do not resample, do not change the seed. Correct "
                    "the implementation and rerun this job identically."
                )
            return (
                ComponentOutcome(
                    component.component_id,
                    component.demand_ids,
                    status,
                    0,
                    0,
                    None,
                    None,
                ),
                None,
                None,
            )
        valuations = [value_group(self.world, forced, plan.group) for plan in plans]
        for valuation in valuations:
            if valuation.residual != 0:
                raise Refusal("receipt decomposition did not close exactly")
        entry = specification(self.policy)
        if entry.applies_affordability:
            keep = [
                (plan, valuation)
                for plan, valuation in zip(plans, valuations)
                if self.ledger.is_affordable(valuation).affordable
            ]
        else:
            keep = list(zip(plans, valuations))
        if not keep:
            return (
                ComponentOutcome(
                    component.component_id,
                    component.demand_ids,
                    STATUS_ALL_UNAFFORDABLE,
                    len(plans),
                    0,
                    None,
                    None,
                ),
                None,
                None,
            )
        values = [valuation.group_ebu for _, valuation in keep]
        index = choose(
            self.policy,
            len(keep),
            values if entry.reads_ebu_to_choose else None,
            self._actor_counter(ordinal),
        )
        plan, valuation = keep[index]
        return (
            ComponentOutcome(
                component.component_id,
                component.demand_ids,
                STATUS_EXECUTED,
                len(plans),
                len(keep),
                plan.plan_id,
                valuation.group_ebu,
            ),
            plan,
            valuation.group_ebu,
        )

    def _require_resolved(self, state, physical, economic, stage: str) -> None:
        """Registered Study-1 semantics: an undecided search invalidates the job.

        `SEARCH_UNRESOLVED` is not scarcity, not incompatibility, not a
        rejection and not a no-action. It is a statement that the computation
        failed to establish something the registered design requires to be
        established, so the job produced no valid data at all. The declared
        Study-1 domain makes it impossible -- the complete plan space fits
        inside the exhaustive budget -- so reaching here means the
        implementation, not the physics, is wrong.
        """
        if not self.registered:
            return
        undecided = unresolved_ids(self.world, state, physical, tuple(economic))
        if undecided:
            raise JobInvalid(
                f"SEARCH_UNRESOLVED at epoch {self.epoch} ({stage}) in registered "
                f"job {self.run_id} for {sorted(undecided)}. The entire job is "
                "invalid: do not continue the trajectory, do not exclude the "
                "epoch, do not resample, do not change the seed. Correct the "
                "implementation and rerun this job identically."
            )

    def _check_decomposition(self, state, active, found) -> str:
        """Verify the epoch against the policy-conditioned global reference.

        The authority is `oracle.global_policy_reference`, built from this
        exact state, these active demands, **these balances and this policy**.
        A proved-blocked part contributes no action; a part whose every plan
        is EBU-unaffordable likewise contributes none and keeps its demand
        pending; every remaining part contributes exactly one plan chosen by
        the policy. Decomposition into demand components is a computational
        factorization and may not define any of that.

        All four levels run, and they are **policy-conditioned**: the physical
        plan set, then the affordable set under this run's balances, then the
        selection law this policy induces over canonical plan identities, then
        the modeled-outcome law that law pushes forward. Level A alone is not
        a runtime verification -- an EBU arm never samples from the
        pre-affordability set, so comparing only that would check a
        distribution the model does not have.

        Off by default: exponential in the number of live routes, and a
        conformance instrument rather than part of the mechanism.
        """
        if not self.decomposition_gate or not found:
            return DECOMPOSITION_NOT_CHECKED
        bound = action_bound(self.world, state)
        if bound == 0:
            return DECOMPOSITION_VERIFIED
        ok, detail = policy_levels(
            self.world, state, active.all, self.ledger, self.policy, bound
        )
        if not ok:
            raise Refusal(
                f"{DECOMPOSITION_DEFECT} at epoch {self.epoch}: the component "
                f"path and the decomposition-free policy-conditioned reference "
                f"disagree ({detail}). Decomposition is an optimization and may "
                "not define what the epoch can do."
            )
        return DECOMPOSITION_VERIFIED

    def run_epoch(self) -> EpochRecord:
        world = self.world
        potential = world.potential
        before = self.state
        potential_before = potential.value_total(before)

        event = self.disturbance.draw(world, before, self.natural_seed, self.epoch)
        forced = apply_disturbance(world, before, event)
        potential_forced = potential.value_total(forced)
        external = potential_forced - potential_before

        # An external event is counted when nature actually moved stock, never
        # inferred from the potential it happened to change. Two disturbances
        # can cancel in `V`, or permute stock at constant `V`, and an interval
        # containing either is not actor-only. See `cycles`.
        epoch_events: tuple[str, ...] = ()
        if forced != before:
            epoch_events = (
                f"ext:t={self.epoch}:{event.source}->{event.destination}"
                f":q={event.quantity}",
            )
            self.external_events.extend(epoch_events)

        physical = derive_physical_demands(world, forced)
        incoming = self.arrivals.arrivals(world, self.arrival_seed, self.epoch)
        for demand in incoming:
            self.arrival_ledger[demand.demand_id] = ArrivalOutcome(
                demand.demand_id,
                demand.resource,
                demand.quantity,
                demand.destination,
                self.epoch,
                LIFECYCLE_ARRIVED,
            )

        # A registered Study-1 job requires every serviceability question it
        # asks to be *decided*. Admission may admit only what is proved
        # serviceable, and an undecided search is neither an admission nor a
        # rejection -- it is a computational integrity failure that invalidates
        # the job. Checked before admission, so the failure is reported at the
        # question that could not be answered rather than at its consequence.
        self._require_resolved(forced, physical, self.held + incoming, "admission")

        decision: AdmissionDecision | None = None
        admitted: tuple[EconomicDemand, ...] = ()
        rejected: tuple[tuple[str, str], ...] = ()
        if incoming:
            admitted, refused, decision = admit(
                world, forced, physical, self.held, incoming, self.admission_seed, self.epoch
            )
            rejected = tuple((demand.demand_id, demand.status) for demand in refused)
            for demand in admitted:
                self.arrival_ledger[demand.demand_id] = self.arrival_ledger[
                    demand.demand_id
                ].at(LIFECYCLE_ADMITTED)
            for demand in refused:
                self.arrival_ledger[demand.demand_id] = self.arrival_ledger[
                    demand.demand_id
                ].at(_REJECTION_LIFECYCLE[demand.status], self.epoch)
        self.held = tuple(sorted(self.held + admitted, key=lambda d: d.demand_id))

        active = ActiveDemandSet.of(physical, self.held)
        self._require_resolved(forced, physical, self.held, "service")
        found = components(world, forced, active)
        decomposition = self._check_decomposition(forced, active, found)

        outcomes: list[ComponentOutcome] = []
        selected: list[ServicePlan] = []
        component_ebu = Fraction(0)
        for ordinal, component in enumerate(found):
            plans = enumerate_service_plans(world, forced, component)
            outcome, plan, value = self._select(component, plans, ordinal, forced)
            outcomes.append(outcome)
            if plan is not None:
                selected.append(plan)
                component_ebu += value

        combined = PlanGroup.of(
            *[action for plan in selected for action in plan.group.actions]
        )
        gate = GATE_CLOSED
        separability = Fraction(0)
        if selected:
            verdict = can_happen_now(world, forced, combined)
            if not verdict.executable:
                raise Refusal(
                    f"{GATE_DEFECT}: independent component plans collide physically "
                    f"({verdict.reason} at {verdict.offending})"
                )
            joint = value_group(world, forced, combined)
            if joint.residual != 0:
                raise Refusal("combined receipt decomposition did not close exactly")
            separability = joint.group_ebu - component_ebu
            if separability != 0:
                raise Refusal(
                    f"{GATE_DEFECT}: combined EBU {joint.group_ebu} differs from the "
                    f"component sum {component_ebu}"
                )
            per_component = {}
            for plan in selected:
                for action, receipt in value_group(world, forced, plan.group).receipts:
                    per_component[action.action_id] = receipt
            for action, receipt in joint.receipts:
                if per_component[action.action_id] != receipt:
                    raise Refusal(
                        f"{GATE_DEFECT}: receipt for {action.action_id} changed when "
                        "independent components were combined"
                    )
            affordability = self.ledger.is_affordable(joint)
            if not affordability.affordable:
                raise Refusal(
                    f"{GATE_DEFECT}: components affordable apart are unaffordable together "
                    f"for owners {affordability.deficient_owners}"
                )
            receipts = tuple((action.action_id, receipt) for action, receipt in joint.receipts)
            owner_deltas = joint.owner_deltas
            epoch_ebu = joint.group_ebu
        else:
            receipts = ()
            owner_deltas = ()
            epoch_ebu = Fraction(0)

        increment = combined.increment(world.dimension)
        after = add(forced, increment)
        balance_before = self.ledger.total
        self.ledger = self.ledger.settle(dict(owner_deltas))
        self.state = after
        potential_after = potential.value_total(after)
        self.external_total += external

        # Service is decided over the whole requirement set, never one demand
        # at a time: separate orders at one destination are additive, so a
        # two-unit delivery does not serve two two-unit orders.
        served = served_economic_ids(requirements(self.held), increment)
        unaffordable = tuple(
            demand_id
            for outcome in outcomes
            if outcome.status == STATUS_ALL_UNAFFORDABLE
            for demand_id in outcome.demand_ids
            if demand_id.startswith("E:")
        )
        unresolved = tuple(
            demand_id
            for outcome in outcomes
            if outcome.status in (
                STATUS_NO_COMPLETE_PLAN,
                STATUS_SEARCH_INCOMPLETE,
                STATUS_SEARCH_UNRESOLVED,
            )
            for demand_id in outcome.demand_ids
            if demand_id.startswith("E:")
        )
        for demand_id in served:
            self.arrival_ledger[demand_id] = self.arrival_ledger[demand_id].at(
                LIFECYCLE_SERVED, self.epoch
            )
        still_held = {d.demand_id for d in self.held} - set(served)
        for demand_id in sorted(still_held):
            if demand_id in unaffordable:
                state = LIFECYCLE_ADMITTED_BUT_EBU_UNAFFORDABLE
            elif demand_id in unresolved:
                state = LIFECYCLE_ADMITTED_BUT_UNRESOLVED_PHYSICAL
            else:
                state = LIFECYCLE_ADMITTED
            self.arrival_ledger[demand_id] = self.arrival_ledger[demand_id].at(state)
        self.held = tuple(demand for demand in self.held if demand.demand_id not in served)
        arrival_states = tuple(
            (demand_id, self.arrival_ledger[demand_id].state)
            for demand_id in sorted(
                {d.demand_id for d in incoming}
                | set(served)
                | still_held
            )
        )

        conservation = Fraction(0)
        for resource in world.resources:
            drift = world.resource_total(after, resource) - world.resource_total(before, resource)
            conservation = max(conservation, abs(drift))
        nonnegativity = Fraction(0)
        for value in after:
            if value < 0:
                nonnegativity = max(nonnegativity, -value)
        accounting = (self.ledger.total - balance_before) - epoch_ebu

        if active.is_empty:
            epoch_status = STATUS_NO_ACTIVE_DEMAND
        elif selected:
            epoch_status = STATUS_EXECUTED
        elif any(outcome.status == STATUS_ALL_UNAFFORDABLE for outcome in outcomes):
            epoch_status = STATUS_ALL_UNAFFORDABLE
        elif any(outcome.status == STATUS_SEARCH_UNRESOLVED for outcome in outcomes):
            epoch_status = STATUS_SEARCH_UNRESOLVED
        elif any(outcome.status == STATUS_SEARCH_INCOMPLETE for outcome in outcomes):
            epoch_status = STATUS_SEARCH_INCOMPLETE
        else:
            epoch_status = STATUS_NO_COMPLETE_PLAN

        record = EpochRecord(
            self.run_id,
            code_identity(),
            self.policy,
            self.epoch,
            before,
            forced,
            after,
            event.status,
            epoch_events,
            external,
            potential_before,
            potential_forced,
            potential_after,
            tuple(demand.demand_id for demand in incoming),
            decision,
            tuple(demand.demand_id for demand in admitted),
            rejected,
            tuple(demand.demand_id for demand in physical),
            tuple(demand.demand_id for demand in active.economic),
            tuple(outcomes),
            combined.group_id,
            tuple(
                sorted(
                    (entry for plan in selected for entry in plan.provenance),
                    key=lambda entry: entry[0],
                )
            ),
            epoch_ebu,
            receipts,
            owner_deltas,
            self.ledger.balances,
            self.ledger.total,
            served,
            unaffordable,
            unresolved,
            arrival_states,
            gate,
            accounting,
            conservation,
            nonnegativity,
            separability,
            epoch_status,
            decomposition,
        )
        if record.accounting_residual != 0:
            raise Refusal(f"accounting residual {record.accounting_residual} is not zero")
        if record.conservation_residual != 0:
            raise Refusal(f"conservation residual {record.conservation_residual} is not zero")
        if record.nonnegativity_residual != 0:
            raise Refusal("a stock went negative")

        # Contract section 21: the cached P-demand representation is discarded
        # here. The next epoch re-derives it from `self.state`, so a shortfall
        # that has been resolved cannot survive as a stale obligation.
        self.records.append(record)
        self.epoch += 1
        return record

    def run(self, epochs: int) -> tuple[EpochRecord, ...]:
        for _ in range(epochs):
            self.run_epoch()
        return tuple(self.records)

    @property
    def capacity_source_residual(self) -> Fraction:
        """B_total(T) - B_total(0) - [V(x_0) - V(x_T) + sum_t dV_ext].

        Exactly zero whenever the run is internally consistent. See `cycles`.
        """
        final = self.world.potential.value_total(self.state)
        return self.ledger.total - (
            self.initial_potential - final + self.external_total
        )
