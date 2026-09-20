"""Four-policy transition harness with mandatory action semantics.

Same canonical ten-phase Gaussian event order as
`EBU-GAUSSIAN-EVENT-PROFILE-v1`, with the single-arm chooser replaced by the
four declared actor policies. `gaussian_harness` is imported unchanged; its
pinned code identity is what makes the registered Stage-A and Stage-B artifacts
replayable, so not one byte of it is touched.

Mandatory action (mission section 6), frozen for every arm
----------------------------------------------------------

If at least one nonempty physically feasible candidate group exists, one group
MUST execute. There is no abstain, wait or no-op candidate, and the empty group
is absent from the menu. Two distinct non-execution outcomes exist and are kept
apart, because conflating them would let an affordability refusal masquerade as
a physical impossibility:

    PHYSICAL_NO_ACTION_AVAILABLE   no nonempty group is physically feasible
    AFFORDABILITY_BLOCKED          groups are feasible but none is affordable

Only the first is genuine absence of a physically feasible action. The second
is an affordability-specific outcome and is reported as such.

Capacity version
----------------

Capacity V1 (`gaussian_harness.capacity`), unchanged, exactly as registered in
Stage A and Stage B. The question isolated here is actor response to the EBU
signal, so the capacity semantics, forcing law and field model are all held
fixed (mission section 8). Capacity V2 is deliberately not substituted.

Capacity never changes EBU measurement (mission section 9): balances enter the
affordability projection and nothing else. `value_group` is called on the
frozen pre-state before any ledger is consulted, and its result is not a
function of the ledger -- asserted by metamorphic test, not by comment.

This module advances model state. It is a transition execution class.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Sequence

from gaussian_harness.actions import EMPTY_GROUP, ActionGroup
from gaussian_harness.candidates import MenuSpecification, candidate_groups
from gaussian_harness.capacity import CapacityLedger, SignedShadowLedger
from gaussian_harness.feasibility import PhysicalRules, assess
from gaussian_harness.forcing import (
    ForcingIncrement,
    accounting_residual,
    apply_forcing,
    conservation_residual,
    external_deviation,
    nonnegative_state_residual,
)
from gaussian_harness.harness import TickBudget
from gaussian_harness.numerics import Refusal, Vector, add, exact, total
from gaussian_harness.potential import LocalGaussianPotential
from gaussian_harness.rng import STREAM_ACTOR, STREAM_FORCING, Counter, exact_residue, uniform_index
from gaussian_harness.valuation import GroupValuation, value_group

from .policies import POLICIES, PolicyDecision, choose
from .region import ConservationLaw, ReferenceRegion

PROFILE_ID = "EBU-GAUSSIAN-HOMEOSTASIS-PROFILE-v1"

STATUS_EXECUTED = "EXECUTED"
STATUS_PHYSICAL_NO_ACTION = "PHYSICAL_NO_ACTION_AVAILABLE"
STATUS_AFFORDABILITY_BLOCKED = "AFFORDABILITY_BLOCKED"
# A declared shock event, in which the actor is never invited to choose. It is
# kept distinct from both non-execution statuses above: absence of execution
# here is a property of the protocol, not of feasibility or affordability.
STATUS_FORCING_ONLY = "FORCING_ONLY"
NON_EXECUTION_STATUSES = (STATUS_PHYSICAL_NO_ACTION, STATUS_AFFORDABILITY_BLOCKED)

MENU_WITH_NET_ZERO = "with_net_zero_groups"
MENU_STRICT_PHYSICAL = "strict_physical_change"
DECLARED_MENU_RULES = (MENU_WITH_NET_ZERO, MENU_STRICT_PHYSICAL)

FORCING_APPLIED = "APPLIED"
FORCING_NULL = "NULL_FORCING"
FORCING_NOT_SCHEDULED = "NOT_SCHEDULED"

# Draw addresses on the forcing stream. The edge draw keeps Stage-B's exact
# coordinates so that the p_force = 1 load reproduces the Stage-B environmental
# process tick for tick; the load gate is added at a fresh index so it cannot
# perturb it.
DRAW_FORCING_EDGE = 0
DRAW_FORCING_GATE = 2
GATE_DENOMINATOR = 4


def code_identity() -> str:
    digest = hashlib.sha256()
    for path in sorted(Path(__file__).parent.glob("*.py")):
        digest.update(path.name.encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


@dataclass(frozen=True)
class ForcingLoad:
    """A declared disturbance load: frequency varies, amplitude does not.

    Mission section 12 varies frequency rather than amplitude, so the physical
    quantum stays `q0` and only the per-tick scheduling probability changes.
    The three declared probabilities all have denominator 4, so one uniform
    residue modulo 4 realizes every load exactly, and the schedules are
    *nested*: every tick forced at 1/4 is also forced at 1/2 and at 1. Loads
    are therefore coupled rather than independent, which removes schedule
    mismatch from the load comparison.
    """

    load_id: str
    probability: Fraction
    quantum: Fraction

    def __post_init__(self) -> None:
        if not 0 < self.probability <= 1:
            raise Refusal("forcing probability must lie in (0, 1]")
        threshold = self.probability * GATE_DENOMINATOR
        if threshold.denominator != 1:
            raise Refusal(
                f"forcing probability {self.probability} is not realizable exactly "
                f"on the declared denominator {GATE_DENOMINATOR}"
            )
        if self.quantum <= 0:
            raise Refusal("forcing quantum must be positive")

    @classmethod
    def declare(cls, load_id: str, probability, quantum=1) -> "ForcingLoad":
        return cls(load_id, exact(probability, "probability"), exact(quantum, "quantum"))

    @property
    def gate_threshold(self) -> int:
        return int(self.probability * GATE_DENOMINATOR)


LOAD_MILD = ForcingLoad.declare("p_force_1_4", Fraction(1, 4))
LOAD_MEDIUM = ForcingLoad.declare("p_force_1_2", Fraction(1, 2))
LOAD_CONTINUOUS = ForcingLoad.declare("p_force_1", Fraction(1))
DECLARED_LOADS = (LOAD_MILD, LOAD_MEDIUM, LOAD_CONTINUOUS)


@dataclass(frozen=True)
class PolicyWorld:
    """One physical world plus the actor policy that acts in it."""

    study_id: str
    configuration_id: str
    potential: LocalGaussianPotential
    rules: PhysicalRules
    menu: MenuSpecification
    initial_state: Vector
    declared_mass: Fraction
    region: ReferenceRegion
    policy: str
    menu_rule: str = MENU_WITH_NET_ZERO

    def __post_init__(self) -> None:
        if self.policy not in POLICIES:
            raise Refusal(f"undeclared actor policy {self.policy!r}")
        if self.menu_rule not in DECLARED_MENU_RULES:
            raise Refusal(f"undeclared menu rule {self.menu_rule!r}")
        if len(self.initial_state) != self.rules.cells:
            raise Refusal("initial state dimension does not match the world")
        if self.potential.dimension != self.rules.cells:
            raise Refusal("potential dimension does not match the world")
        if total(self.initial_state) != self.declared_mass:
            raise Refusal("initial state does not carry the declared mass")

    @classmethod
    def declare(
        cls,
        study_id: str,
        configuration_id: str,
        reference: Sequence,
        scale: Sequence,
        quanta: Sequence,
        policy: str,
        max_group_size: int = 2,
        initial_state: Sequence | None = None,
        menu_rule: str = MENU_WITH_NET_ZERO,
    ) -> "PolicyWorld":
        potential = LocalGaussianPotential.declare(reference, scale)
        rules = PhysicalRules.complete_graph(potential.dimension)
        menu = MenuSpecification.declare(quanta, max_group_size)
        start = potential.reference if initial_state is None else tuple(
            exact(value, "initial_state") for value in initial_state
        )
        mass = Fraction(0)
        for value in start:
            mass += value
        law = ConservationLaw.total_mass(potential.dimension, mass)
        region = ReferenceRegion.derive(potential, [law])
        return cls(
            study_id, configuration_id, potential, rules, menu, start, mass, region,
            policy, menu_rule,
        )

    def with_policy(self, policy: str) -> "PolicyWorld":
        return PolicyWorld(
            self.study_id,
            self.configuration_id,
            self.potential,
            self.rules,
            self.menu,
            self.initial_state,
            self.declared_mass,
            self.region,
            policy,
            self.menu_rule,
        )

    def candidates(self) -> tuple[ActionGroup, ...]:
        """The declared menu, in canonical order.

        Generation is EBU-blind and state-independent; the menu rule removes
        net-zero groups structurally rather than letting a policy avoid them.
        """
        groups = candidate_groups(self.rules, self.menu)
        if self.menu_rule == MENU_WITH_NET_ZERO:
            return groups
        return tuple(
            group for group in groups
            if any(value != 0 for value in group.increment(self.rules.cells))
        )

    @property
    def applies_affordability(self) -> bool:
        return POLICIES[self.policy].applies_affordability


@dataclass(frozen=True)
class PolicyTickRecord:
    """One replayable tick. Physical-state homeostasis fields are separate."""

    policy: str
    tick: int
    state_before: Vector
    forcing_status: str
    raw_forcing: str | None
    applied_forcing: str | None
    state_frozen: Vector
    n_candidates: int
    n_feasible: int
    n_affordable: int
    chosen_id: str
    null_action: bool
    chosen_ebu: Fraction | None
    selection_rule: str | None
    tie_size: int
    actor_provenance: str | None
    receipts: tuple[tuple[str, Fraction], ...]
    state_after: Vector
    # physical-state homeostasis observables
    potential_total: Fraction
    radial_square: Fraction
    in_h95: bool
    in_h99: bool
    # accounting observables, never part of any homeostasis metric
    balances: tuple[Fraction, ...]
    balance_total: Fraction
    audit_ledger: Fraction
    external_deviation: Fraction
    conservation_residual: Fraction
    accounting_residual: Fraction
    nonnegativity_residual: Fraction
    status: str


def _ledger_for(world: PolicyWorld):
    cells = world.rules.cells
    return CapacityLedger.zero(cells) if world.applies_affordability else SignedShadowLedger.zero(cells)


@dataclass
class PolicyRun:
    """Mutable run state for one policy in one world."""

    world: PolicyWorld
    forcing_seed: int
    actor_seed: int
    budget: TickBudget = field(default_factory=TickBudget.conformance)
    state: Vector = field(init=False)
    ledger: object = field(init=False)
    audit: Fraction = field(init=False)
    accounting_constant: Fraction = field(init=False)
    tick: int = field(init=False, default=0)
    records: list[PolicyTickRecord] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        self.state = self.world.initial_state
        self.ledger = _ledger_for(self.world)
        self.audit = Fraction(0)
        # The driven identity is `V + sum_i B_i - J = K`, and K is fixed by the
        # initial condition, not by fiat: with B(0) = 0 and J(0) = 0 it is
        # V(x_0). Stage A and Stage B both start exactly at the reference, so
        # K = 0 there and the pinned harness hard-codes it; a world started off
        # the reference needs the real constant or every residual is reported
        # as V(x_0).
        self.accounting_constant = self.world.potential.value_total(self.state)

    @property
    def run_id(self) -> str:
        preimage = "|".join(
            (
                PROFILE_ID,
                self.world.study_id,
                self.world.configuration_id,
                self.world.policy,
                str(self.forcing_seed),
                str(self.actor_seed),
                code_identity(),
            )
        )
        return hashlib.sha256(preimage.encode("utf-8")).hexdigest()[:32]

    def _counter(self, stream_id: str, event_index: int, draw_index: int) -> Counter:
        seed = self.forcing_seed if stream_id == STREAM_FORCING else self.actor_seed
        return Counter(
            self.world.study_id,
            self.world.configuration_id,
            seed,
            stream_id,
            self.tick,
            event_index,
            draw_index,
        )

    def scheduled_forcing(self, load: ForcingLoad | None) -> ForcingIncrement | None:
        """The raw environmental proposal for this tick, before admissibility.

        Reads the forcing stream and the declared topology only. It cannot see
        the state, the balances, the potential or the actor stream, so the raw
        environmental process is identical across every arm sharing a seed.
        """
        if load is None:
            return None
        gate = exact_residue(self._counter(STREAM_FORCING, 0, DRAW_FORCING_GATE), GATE_DENOMINATOR)
        if gate.draw_status != "READY" or gate.residue is None:
            raise Refusal("TERMINAL_REJECTION_CAP on the forcing load gate")
        if gate.residue >= load.gate_threshold:
            return None
        edges = tuple(sorted(self.world.rules.edges))
        index, _ = uniform_index(self._counter(STREAM_FORCING, 0, DRAW_FORCING_EDGE), len(edges))
        source, destination = edges[index]
        return ForcingIncrement(source, destination, load.quantum)

    def run_tick(
        self,
        load: ForcingLoad | None = None,
        shock: ForcingIncrement | None = None,
        actor_enabled: bool = True,
    ) -> PolicyTickRecord:
        """One tick of the canonical event order.

        `shock` injects a declared conservative disturbance instead of drawing
        one from the load schedule, and `actor_enabled=False` runs forcing and
        audit only. Together they express a pure shock event, so a recovery
        trial of `H` post-shock actor ticks is exactly `H` and the potential
        immediately after the shock is the declared disturbance rather than a
        state an actor has already moved.
        """
        if load is not None and shock is not None:
            raise Refusal("a tick carries either a scheduled load or a declared shock")
        if self.tick >= self.budget.limit:
            raise Refusal(
                f"TICK_BUDGET_EXHAUSTED: {self.budget.authorization} admits "
                f"{self.budget.limit} ticks"
            )
        world = self.world
        potential = world.potential
        cells = world.rules.cells
        state_before = self.state

        # Phase 1: external forcing. Nature moves x and never credits a balance.
        proposal = shock if shock is not None else self.scheduled_forcing(load)
        applied: ForcingIncrement | None = None
        if proposal is None:
            forcing_status = FORCING_NOT_SCHEDULED
        elif state_before[proposal.source] >= proposal.magnitude:
            applied = proposal
            forcing_status = FORCING_APPLIED
        else:
            # Per-arm admissibility. No resample, clip, reversal, substitution
            # or magnitude change: the draw is simply not realizable here.
            forcing_status = FORCING_NULL

        deviation = Fraction(0)
        if applied is not None:
            moved = apply_forcing(state_before, applied)
            deviation = external_deviation(potential, state_before, moved)
            self.audit += deviation
            self.state = moved

        # Phase 2: freeze the physical pre-action state.
        frozen = self.state

        # Phase 3: EBU-blind candidate generation.
        candidates = world.candidates()

        # Phase 4: physical feasibility, decided before and without EBU.
        feasible = [
            group for group in candidates if assess(world.rules, frozen, group).feasible
        ]

        # Phase 5: exact EBU valuation of every feasible group. In the control
        # arm this is measurement only and never reaches the chooser.
        valuations: list[GroupValuation] = [
            value_group(potential, frozen, group) for group in feasible
        ]

        # Phase 6: capacity affordability. Only the EBU arms filter on it.
        if world.applies_affordability:
            admissible = [
                valuation
                for valuation in valuations
                if self.ledger.project(valuation.owner_deltas).affordable
            ]
        else:
            admissible = list(valuations)

        # Phase 7: policy choice under mandatory action.
        decision: PolicyDecision | None = None
        if not actor_enabled:
            status = STATUS_FORCING_ONLY
            chosen = None
        elif not feasible:
            status = STATUS_PHYSICAL_NO_ACTION
            chosen = None
        elif not admissible:
            status = STATUS_AFFORDABILITY_BLOCKED
            chosen = None
        else:
            counter = self._counter(STREAM_ACTOR, 1, 0)
            decision = choose(
                world.policy,
                tuple(valuation.group_ebu for valuation in admissible),
                counter,
            )
            chosen = admissible[decision.index]
            status = STATUS_EXECUTED

        # Phases 8 and 9: execute exactly the valued group, then settle once.
        if chosen is None:
            chosen_group: ActionGroup = EMPTY_GROUP
            receipts: tuple[tuple[str, Fraction], ...] = ()
            chosen_ebu = None
        else:
            chosen_group = chosen.group
            if chosen.residual != 0:
                raise Refusal(
                    f"RECEIPT_CLOSURE_FAILURE: residual {chosen.residual} on "
                    f"{chosen_group.group_id}"
                )
            receipts = tuple(
                (action.action_id, receipt) for action, receipt in chosen.receipts
            )
            chosen_ebu = chosen.group_ebu
            self.state = add(frozen, chosen_group.increment(cells))
            self.ledger = self.ledger.settle(chosen.owner_deltas)

        # Phase 10: audit, independent of every runtime decision above.
        radial = world.region.radial_square(self.state)
        record = PolicyTickRecord(
            policy=world.policy,
            tick=self.tick,
            state_before=state_before,
            forcing_status=forcing_status,
            raw_forcing=proposal.forcing_id if proposal is not None else None,
            applied_forcing=applied.forcing_id if applied is not None else None,
            state_frozen=frozen,
            n_candidates=len(candidates),
            n_feasible=len(feasible),
            n_affordable=len(admissible),
            chosen_id=chosen_group.group_id,
            null_action=(
                status == STATUS_EXECUTED
                and all(value == 0 for value in chosen_group.increment(cells))
            ),
            chosen_ebu=chosen_ebu,
            selection_rule=decision.rule if decision is not None else None,
            tie_size=decision.tie_size if decision is not None else 0,
            actor_provenance=decision.provenance if decision is not None else None,
            receipts=receipts,
            state_after=self.state,
            potential_total=potential.value_total(self.state),
            radial_square=radial,
            in_h95=world.region.contains_radial_square(radial, "H95"),
            in_h99=world.region.contains_radial_square(radial, "H99"),
            balances=self.ledger.balances,
            balance_total=self.ledger.total,
            audit_ledger=self.audit,
            external_deviation=deviation,
            conservation_residual=conservation_residual(self.state, world.declared_mass),
            accounting_residual=accounting_residual(
                potential, self.state, self.ledger, self.audit, self.accounting_constant
            ),
            nonnegativity_residual=nonnegative_state_residual(self.state),
            status=status,
        )
        self.records.append(record)
        self.tick += 1
        return record


def run_trajectory(
    world: PolicyWorld,
    forcing_seed: int,
    actor_seed: int,
    horizon: int,
    load: ForcingLoad | None,
    budget: TickBudget | None = None,
) -> PolicyRun:
    """Advance `horizon` ticks under a declared forcing load."""
    if horizon < 1:
        raise Refusal("horizon must be at least one tick")
    run = PolicyRun(world, forcing_seed, actor_seed, budget or TickBudget.conformance())
    for _ in range(horizon):
        run.run_tick(load)
    return run
