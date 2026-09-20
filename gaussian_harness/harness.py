"""Controlled transition harness implementing the canonical Gaussian event order.

Profile `EBU-GAUSSIAN-EVENT-PROFILE-v1`, ten phases per tick:

    external forcing -> freeze physical pre-action state -> generate physical
    candidate groups -> physical feasibility -> exact EBU valuation -> capacity
    affordability -> seeded random actor choice -> exact execution -> capacity
    settlement -> audit

EBU calculates. EBU does not choose. The chooser receives opaque candidate
identities and a count, never a value, sign, potential, marginal, distance or
balance. There is no max-EBU, minimum-V, service-first, least-harmful,
preservation, gradient-following or hidden restorative fallback path.

This harness advances model state. It is a transition execution class, not a
static check, and running it is not a scientific result.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Sequence

from .actions import EMPTY_GROUP, ActionGroup
from .candidates import MenuSpecification, candidate_groups
from .capacity import CapacityLedger, SignedShadowLedger
from .feasibility import PhysicalRules, assess
from .forcing import (
    ForcingIncrement,
    accounting_residual,
    apply_forcing,
    conservation_residual,
    external_deviation,
    nonnegative_state_residual,
)
from .numerics import Refusal, Vector, add, total
from .potential import LocalGaussianPotential
from .rng import STREAM_ACTOR, STREAM_FORCING, Counter, uniform_index
from .valuation import GroupValuation, value_group

ARM_EBU = "ebu_affordability_random_actor"
ARM_CONTROL = "physical_feasibility_random_actor"
DECLARED_ARMS = (ARM_EBU, ARM_CONTROL)

STATUS_EXECUTED = "EXECUTED"
STATUS_DEADLOCK = "DEADLOCK"
STATUS_IDLE = "IDLE"
STATUS_FORCING_ONLY = "FORCING_ONLY"

_PHASE_ORDER = (
    "external_forcing",
    "freeze_pre_action_state",
    "generate_candidate_groups",
    "physical_feasibility",
    "exact_ebu_valuation",
    "capacity_affordability",
    "seeded_random_actor_choice",
    "exact_execution",
    "capacity_settlement",
    "audit",
)


def code_identity() -> str:
    """SHA-256 over the package sources, so a log pins the code that made it."""
    digest = hashlib.sha256()
    for path in sorted(Path(__file__).parent.glob("*.py")):
        digest.update(path.name.encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


@dataclass(frozen=True)
class WorldConfiguration:
    """Everything needed to reproduce a run except the two seeds."""

    study_id: str
    configuration_id: str
    potential: LocalGaussianPotential
    rules: PhysicalRules
    menu: MenuSpecification
    initial_state: Vector
    declared_mass: Fraction
    arm: str = ARM_EBU

    def __post_init__(self) -> None:
        if self.arm not in DECLARED_ARMS:
            raise Refusal(f"undeclared arm {self.arm!r}")
        if len(self.initial_state) != self.rules.cells:
            raise Refusal("initial state dimension does not match the world")
        if self.potential.dimension != self.rules.cells:
            raise Refusal("potential dimension does not match the world")
        if total(self.initial_state) != self.declared_mass:
            raise Refusal("initial state does not carry the declared mass")

    def with_arm(self, arm: str) -> "WorldConfiguration":
        return WorldConfiguration(
            self.study_id,
            self.configuration_id,
            self.potential,
            self.rules,
            self.menu,
            self.initial_state,
            self.declared_mass,
            arm,
        )


@dataclass(frozen=True)
class TickRecord:
    """One fully replayable event record. Aggregates alone are never stored."""

    run_id: str
    configuration_id: str
    code_id: str
    arm: str
    tick: int
    state_before: Vector
    forcing: str | None
    forcing_provenance: str | None
    state_frozen: Vector
    local_potential: tuple[Fraction, ...]
    audit_potential: Fraction
    candidate_ids: tuple[str, ...]
    feasible_ids: tuple[str, ...]
    infeasible_reasons: tuple[tuple[str, str], ...]
    ebu_values: tuple[tuple[str, Fraction], ...]
    projected_balances: tuple[tuple[str, tuple[tuple[int, Fraction], ...]], ...]
    affordable_ids: tuple[str, ...]
    chosen_id: str
    actor_provenance: str | None
    receipts: tuple[tuple[str, Fraction], ...]
    state_after: Vector
    balances: tuple[Fraction, ...]
    balance_total: Fraction
    audit_ledger: Fraction
    conservation_residual: Fraction
    accounting_residual: Fraction
    nonnegativity_residual: Fraction
    status: str


@dataclass(frozen=True)
class TickBudget:
    """Structural ceiling on how many ticks a run may advance.

    Task section 27: the harness existing is not permission to execute a long
    study. A conformance budget is small and self-authorizing; anything larger
    must name a frozen preregistration, and since no preregistration is frozen
    yet, `registered_study` fails closed on an empty identifier.
    """

    limit: int
    authorization: str

    def __post_init__(self) -> None:
        if self.limit < 1:
            raise Refusal("tick budget must admit at least one tick")
        if not self.authorization:
            raise Refusal("tick budget needs an explicit authorization label")

    @classmethod
    def conformance(cls, limit: int = 64) -> "TickBudget":
        if limit > 64:
            raise Refusal(
                "conformance budget is capped at 64 ticks; a longer run needs a "
                "frozen preregistration via TickBudget.registered_study"
            )
        return cls(limit, "CONFORMANCE-ONLY-NOT-A-STUDY")

    @classmethod
    def registered_study(cls, limit: int, preregistration_id: str) -> "TickBudget":
        if not preregistration_id or not preregistration_id.strip():
            raise Refusal(
                "REGISTERED_STUDY_REFUSED: no frozen preregistration identifier supplied"
            )
        return cls(limit, f"REGISTERED-STUDY:{preregistration_id}")


def _ledger_for(arm: str, cells: int):
    return CapacityLedger.zero(cells) if arm == ARM_EBU else SignedShadowLedger.zero(cells)


@dataclass
class Run:
    """Mutable run state. The only object in the package that changes."""

    configuration: WorldConfiguration
    forcing_seed: int
    actor_seed: int
    budget: TickBudget = field(default_factory=TickBudget.conformance)
    state: Vector = field(init=False)
    ledger: object = field(init=False)
    audit: Fraction = field(init=False)
    tick: int = field(init=False, default=0)
    records: list[TickRecord] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        self.state = self.configuration.initial_state
        self.ledger = _ledger_for(self.configuration.arm, self.configuration.rules.cells)
        self.audit = Fraction(0)

    @property
    def run_id(self) -> str:
        preimage = "|".join(
            (
                self.configuration.study_id,
                self.configuration.configuration_id,
                self.configuration.arm,
                str(self.forcing_seed),
                str(self.actor_seed),
                code_identity(),
            )
        )
        return hashlib.sha256(preimage.encode("utf-8")).hexdigest()[:32]

    def _counter(self, stream_id: str, event_index: int, draw_index: int) -> Counter:
        seed = self.forcing_seed if stream_id == STREAM_FORCING else self.actor_seed
        return Counter(
            self.configuration.study_id,
            self.configuration.configuration_id,
            seed,
            stream_id,
            self.tick,
            event_index,
            draw_index,
        )

    def run_tick(
        self,
        forcing: ForcingIncrement | None = None,
        actor_enabled: bool = True,
    ) -> TickRecord:
        """Execute exactly one tick of the canonical event order.

        With `actor_enabled=False` the tick carries external forcing and the
        audit only: candidates are still enumerated and valued for the record,
        but no action is chosen, executed or settled. This makes a pure shock
        event expressible, so a registered horizon of H post-shock actor ticks
        is exactly H and not H+1, and V immediately after the shock is the
        declared disturbance D rather than a state an actor has already moved.
        """
        if self.tick >= self.budget.limit:
            raise Refusal(
                f"TICK_BUDGET_EXHAUSTED: {self.budget.authorization} admits "
                f"{self.budget.limit} ticks"
            )
        configuration = self.configuration
        potential = configuration.potential
        cells = configuration.rules.cells
        state_before = self.state

        # Phase 1: external forcing. Nature moves x and never credits a balance.
        forcing_provenance = None
        if forcing is not None:
            forcing_provenance = self._counter(STREAM_FORCING, 0, 0).provenance
            moved = apply_forcing(state_before, forcing)
            self.audit += external_deviation(potential, state_before, moved)
            self.state = moved

        # Phase 2: freeze the physical pre-action state. Everything below reads z.
        frozen = self.state

        # Phase 3: EBU-blind candidate generation.
        candidates = candidate_groups(configuration.rules, configuration.menu)

        # Phase 4: physical feasibility, before any valuation.
        feasible: list[ActionGroup] = []
        infeasible: list[tuple[str, str]] = []
        for group in candidates:
            verdict = assess(configuration.rules, frozen, group)
            if verdict.feasible:
                feasible.append(group)
            else:
                infeasible.append((group.group_id, verdict.reason))

        # Phase 5: exact EBU valuation of exactly the feasible groups.
        valuations: list[GroupValuation] = [
            value_group(potential, frozen, group) for group in feasible
        ]

        # Phase 6: capacity affordability. The control arm applies no filter.
        projected: list[tuple[str, tuple[tuple[int, Fraction], ...]]] = []
        allowed: list[GroupValuation] = []
        for valuation in valuations:
            decision = self.ledger.project(valuation.owner_deltas)
            projected.append((valuation.group.group_id, decision.projected))
            if configuration.arm == ARM_EBU:
                if decision.affordable:
                    allowed.append(valuation)
            else:
                allowed.append(valuation)

        # Phase 7: seeded random actor choice over opaque identities only.
        allowed_ids = tuple(valuation.group.group_id for valuation in allowed)
        actor_provenance = None
        if allowed and actor_enabled:
            counter = self._counter(STREAM_ACTOR, 1, 0)
            actor_provenance = counter.provenance
            index, _ = uniform_index(counter, len(allowed_ids))
            chosen = allowed[index]
        else:
            chosen = None

        # Phases 8 and 9: execute exactly the valued group, then settle once.
        if chosen is None:
            chosen_group = EMPTY_GROUP
            receipts: tuple[tuple[str, Fraction], ...] = ()
            if not actor_enabled:
                # A forcing-only event. The actor was never invited to choose,
                # so absence of execution here is not evidence of deadlock.
                status = STATUS_FORCING_ONLY
            else:
                status = (
                    STATUS_DEADLOCK
                    if potential.value_total(frozen) > 0
                    else STATUS_IDLE
                )
        else:
            chosen_group = chosen.group
            receipts = tuple(
                (action.action_id, receipt) for action, receipt in chosen.receipts
            )
            if chosen.residual != 0:
                raise Refusal(
                    f"RECEIPT_CLOSURE_FAILURE: residual {chosen.residual} on {chosen_group.group_id}"
                )
            self.state = add(frozen, chosen_group.increment(cells))
            self.ledger = self.ledger.settle(chosen.owner_deltas)
            status = STATUS_EXECUTED

        # Phase 10: audit. Independent of every runtime decision above.
        record = TickRecord(
            run_id=self.run_id,
            configuration_id=configuration.configuration_id,
            code_id=code_identity(),
            arm=configuration.arm,
            tick=self.tick,
            state_before=state_before,
            forcing=forcing.forcing_id if forcing is not None else None,
            forcing_provenance=forcing_provenance,
            state_frozen=frozen,
            local_potential=tuple(
                potential.factor_value(self.state, index) for index in range(cells)
            ),
            audit_potential=potential.value_total(self.state),
            candidate_ids=tuple(group.group_id for group in candidates),
            feasible_ids=tuple(group.group_id for group in feasible),
            infeasible_reasons=tuple(infeasible),
            ebu_values=tuple(
                (valuation.group.group_id, valuation.group_ebu) for valuation in valuations
            ),
            projected_balances=tuple(projected),
            affordable_ids=allowed_ids,
            chosen_id=chosen_group.group_id,
            actor_provenance=actor_provenance,
            receipts=receipts,
            state_after=self.state,
            balances=self.ledger.balances,
            balance_total=self.ledger.total,
            audit_ledger=self.audit,
            conservation_residual=conservation_residual(self.state, configuration.declared_mass),
            accounting_residual=accounting_residual(
                potential, self.state, self.ledger, self.audit
            ),
            nonnegativity_residual=nonnegative_state_residual(self.state),
            status=status,
        )
        self.records.append(record)
        self.tick += 1
        return record

    def max_residuals(self) -> dict[str, Fraction]:
        worst = {"accounting": Fraction(0), "conservation": Fraction(0), "nonnegativity": Fraction(0)}
        for record in self.records:
            worst["accounting"] = max(worst["accounting"], abs(record.accounting_residual))
            worst["conservation"] = max(worst["conservation"], abs(record.conservation_residual))
            worst["nonnegativity"] = max(
                worst["nonnegativity"], abs(record.nonnegativity_residual)
            )
        return worst
