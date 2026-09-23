"""Capacity-V2 transition harness.

Reuses the registered pure mathematics unchanged — potential, actions,
candidate generation, feasibility, valuation, receipts and the two
counter-addressed RNG streams all come from `gaussian_harness` — and replaces
only the capacity state law.

Event order is the registered profile `EBU-GAUSSIAN-EVENT-PROFILE-v1`, with one
addition required by the new state law: the ceiling is re-imposed after external
forcing, because forcing moves `x` and therefore moves each cell's ceiling.

EBU calculates; EBU does not choose.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path

from gaussian_harness.actions import EMPTY_GROUP, ActionGroup
from gaussian_harness.candidates import MenuSpecification, candidate_groups
from gaussian_harness.feasibility import PhysicalRules, assess
from gaussian_harness.forcing import (
    ForcingIncrement,
    apply_forcing,
    conservation_residual,
    external_deviation,
    nonnegative_state_residual,
)
from gaussian_harness.numerics import Refusal, Vector, add, total
from gaussian_harness.potential import LocalGaussianPotential
from gaussian_harness.rng import STREAM_ACTOR, STREAM_FORCING, Counter, uniform_index
from gaussian_harness.valuation import GroupValuation, value_group

from . import MODEL_IDENTITY
from .ledger import (
    DeviationBoundedLedger,
    SignedShadowLedgerV2,
    ceiling_violation,
    extended_accounting_residual,
)

ARM_V2 = "capacity_v2_affordability_random_actor"
ARM_CONTROL = "physical_feasibility_random_actor"

STATUS_EXECUTED = "EXECUTED"
STATUS_DEADLOCK = "DEADLOCK"
STATUS_IDLE = "IDLE"
STATUS_FORCING_ONLY = "FORCING_ONLY"


def code_identity() -> str:
    """SHA-256 over this package's sources. Distinct from the V1 identity."""
    digest = hashlib.sha256()
    for path in sorted(Path(__file__).parent.glob("*.py")):
        digest.update(path.name.encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


@dataclass(frozen=True)
class V2Configuration:
    study_id: str
    configuration_id: str
    potential: LocalGaussianPotential
    rules: PhysicalRules
    menu: MenuSpecification
    initial_state: Vector
    declared_mass: Fraction
    arm: str = ARM_V2

    def __post_init__(self) -> None:
        if self.arm not in (ARM_V2, ARM_CONTROL):
            raise Refusal(f"undeclared arm {self.arm!r}")
        if total(self.initial_state) != self.declared_mass:
            raise Refusal("initial state does not carry the declared mass")


@dataclass(frozen=True)
class V2TickRecord:
    tick: int
    arm: str
    state_frozen: Vector
    state_after: Vector
    forcing: str | None
    potential_value: Fraction
    balances: tuple[Fraction, ...]
    balance_total: Fraction
    retired: Fraction
    audit_ledger: Fraction
    ceilings: tuple[Fraction, ...]
    candidate_count: int
    feasible_ids: tuple[str, ...]
    affordable_ids: tuple[str, ...]
    ebu_values: tuple[tuple[str, Fraction], ...]
    chosen_id: str
    receipts: tuple[tuple[str, Fraction], ...]
    retired_this_tick: Fraction
    conservation_residual: Fraction
    extended_accounting_residual: Fraction
    ceiling_violation: Fraction
    nonnegativity_residual: Fraction
    status: str
    forcing_provenance: str | None
    actor_provenance: str | None


@dataclass
class V2Run:
    configuration: V2Configuration
    forcing_seed: int
    actor_seed: int
    state: Vector = field(init=False)
    ledger: object = field(init=False)
    audit: Fraction = field(init=False)
    tick: int = field(init=False, default=0)
    records: list[V2TickRecord] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        self.state = self.configuration.initial_state
        cells = self.configuration.rules.cells
        # The control applies no gate, so it needs a ledger that never refuses.
        self.ledger = (
            DeviationBoundedLedger.zero(cells)
            if self.configuration.arm == ARM_V2
            else SignedShadowLedgerV2.zero(cells)
        )
        self.audit = Fraction(0)

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
    ) -> V2TickRecord:
        configuration = self.configuration
        potential = configuration.potential
        cells = configuration.rules.cells
        retired_before = self.ledger.retired

        # Phase 1: external forcing, then re-impose the ceiling it may have moved.
        forcing_provenance = None
        if forcing is not None:
            forcing_provenance = self._counter(STREAM_FORCING, 0, 0).provenance
            moved = apply_forcing(self.state, forcing)
            self.audit += external_deviation(potential, self.state, moved)
            self.state = moved
            self.ledger = self.ledger.reconcile(potential, self.state)

        # Phase 2: freeze the physical pre-action state.
        frozen = self.state

        # Phases 3-5: EBU-blind candidates, physical feasibility, exact valuation.
        candidates = candidate_groups(configuration.rules, configuration.menu)
        feasible: list[ActionGroup] = []
        for group in candidates:
            if assess(configuration.rules, frozen, group).feasible:
                feasible.append(group)
        valuations: list[GroupValuation] = [
            value_group(potential, frozen, group) for group in feasible
        ]

        # Phase 6: affordability. The control applies no filter.
        allowed: list[GroupValuation] = []
        for valuation in valuations:
            if configuration.arm == ARM_V2:
                if self.ledger.project(valuation.owner_deltas).affordable:
                    allowed.append(valuation)
            else:
                allowed.append(valuation)

        # Phase 7: seeded random choice over opaque identities only.
        allowed_ids = tuple(v.group.group_id for v in allowed)
        actor_provenance = None
        chosen = None
        if allowed and actor_enabled:
            counter = self._counter(STREAM_ACTOR, 1, 0)
            actor_provenance = counter.provenance
            index, _ = uniform_index(counter, len(allowed_ids))
            chosen = allowed[index]

        # Phases 8-9: execute exactly the valued group, settle once, apply ceiling.
        if chosen is None:
            chosen_group = EMPTY_GROUP
            receipts: tuple[tuple[str, Fraction], ...] = ()
            if not actor_enabled:
                status = STATUS_FORCING_ONLY
            else:
                status = (
                    STATUS_DEADLOCK if potential.value_total(frozen) > 0 else STATUS_IDLE
                )
        else:
            chosen_group = chosen.group
            if chosen.residual != 0:
                raise Refusal(f"RECEIPT_CLOSURE_FAILURE: {chosen.residual}")
            receipts = tuple((a.action_id, r) for a, r in chosen.receipts)
            self.state = add(frozen, chosen_group.increment(cells))
            self.ledger = self.ledger.settle(chosen.owner_deltas, potential, self.state)
            status = STATUS_EXECUTED

        # Phase 10: audit, independent of every runtime decision above.
        record = V2TickRecord(
            tick=self.tick,
            arm=configuration.arm,
            state_frozen=frozen,
            state_after=self.state,
            forcing=forcing.forcing_id if forcing is not None else None,
            potential_value=potential.value_total(self.state),
            balances=self.ledger.balances,
            balance_total=self.ledger.total,
            retired=self.ledger.retired,
            audit_ledger=self.audit,
            ceilings=tuple(
                potential.factor_value(self.state, index) for index in range(cells)
            ),
            candidate_count=len(candidates),
            feasible_ids=tuple(g.group_id for g in feasible),
            affordable_ids=allowed_ids,
            ebu_values=tuple((v.group.group_id, v.group_ebu) for v in valuations),
            chosen_id=chosen_group.group_id,
            receipts=receipts,
            retired_this_tick=self.ledger.retired - retired_before,
            conservation_residual=conservation_residual(
                self.state, configuration.declared_mass
            ),
            extended_accounting_residual=extended_accounting_residual(
                potential, self.state, self.ledger, self.audit
            ),
            ceiling_violation=ceiling_violation(potential, self.state, self.ledger),
            nonnegativity_residual=nonnegative_state_residual(self.state),
            status=status,
            forcing_provenance=forcing_provenance,
            actor_provenance=actor_provenance,
        )
        self.records.append(record)
        self.tick += 1
        return record

    def max_residuals(self) -> dict[str, Fraction]:
        worst = {
            "extended_accounting": Fraction(0),
            "conservation": Fraction(0),
            "ceiling": Fraction(0),
            "nonnegativity": Fraction(0),
        }
        for record in self.records:
            worst["extended_accounting"] = max(
                worst["extended_accounting"], abs(record.extended_accounting_residual)
            )
            worst["conservation"] = max(
                worst["conservation"], abs(record.conservation_residual)
            )
            worst["ceiling"] = max(worst["ceiling"], abs(record.ceiling_violation))
            worst["nonnegativity"] = max(
                worst["nonnegativity"], abs(record.nonnegativity_residual)
            )
        return worst
