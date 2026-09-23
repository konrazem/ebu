"""Stage-A environment: one conservative shock, then forcing OFF.

Task section 28. The world starts exactly at the reference

    x_0 = x*,  V_0 = 0,  B_i(0) = 0,  J_0 = 0

one conservative shock u_0 = S xi_0 is drawn from the forcing stream, and
thereafter u_t = 0 for every t > 0. The runtime after the shock is random
affordable action selection.

With no further forcing J is constant, so section 29's expected identity

    V(t) + sum_i B_i(t) = D_shock

must hold at every tick. It does **not** imply V(t) -> 0. Recovery is the
scientific question, and this module asserts nothing about it: monotonic
recovery, nonmonotonic recovery, damped oscillation, persistent cycling,
plateau, deadlock and no restoring tendency are all admissible observations.

Building and running this harness is not a registered study. The preregistration
must be frozen before the comparison in section 33 is executed.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Sequence

from .candidates import MenuSpecification
from .feasibility import PhysicalRules
from .forcing import ForcingIncrement
from .harness import (
    ARM_CONTROL,
    ARM_EBU,
    STATUS_DEADLOCK,
    Run,
    TickBudget,
    TickRecord,
    WorldConfiguration,
    code_identity,
)
from .numerics import Refusal, exact, exact_vector
from .potential import LocalGaussianPotential
from .rng import STREAM_FORCING, Counter, uniform_index

STAGE_A_PROTOCOL_ID = "EBU-GAUSSIAN-STAGE-A-SINGLE-SHOCK-v1"


@dataclass(frozen=True)
class ShockSpecification:
    """Declared finite set of conservative shocks the forcing stream may draw."""

    magnitudes: tuple[Fraction, ...]

    def __post_init__(self) -> None:
        if not self.magnitudes:
            raise Refusal("shock specification needs at least one magnitude")
        if any(magnitude <= 0 for magnitude in self.magnitudes):
            raise Refusal("shock magnitudes must be positive")

    @classmethod
    def declare(cls, magnitudes) -> "ShockSpecification":
        return cls(exact_vector(magnitudes, "magnitudes"))


def draw_shock(
    configuration: WorldConfiguration,
    shocks: ShockSpecification,
    forcing_seed: int,
) -> ForcingIncrement:
    """Draw the single Stage-A shock from the forcing stream.

    The draw reads only its own counter coordinates. It cannot observe
    balances, EBU, the potential or the actor stream.
    """
    cells = configuration.rules.cells
    ordered_edges = tuple(sorted(configuration.rules.edges))
    base = Counter(
        configuration.study_id,
        configuration.configuration_id,
        forcing_seed,
        STREAM_FORCING,
        0,
        0,
        0,
    )
    edge_index, _ = uniform_index(base, len(ordered_edges))
    magnitude_index, _ = uniform_index(base.at(draw_index=1), len(shocks.magnitudes))
    source, destination = ordered_edges[edge_index]
    return ForcingIncrement(source, destination, shocks.magnitudes[magnitude_index])


def stage_a_world(
    study_id: str,
    configuration_id: str,
    reference: Sequence,
    scale: Sequence,
    quanta: Sequence,
    max_group_size: int = 2,
    upper_bound=None,
    arm: str = ARM_EBU,
) -> WorldConfiguration:
    """Build a Stage-A world starting exactly at its reference."""
    potential = LocalGaussianPotential.declare(reference, scale)
    cells = potential.dimension
    bound = None if upper_bound is None else exact(upper_bound, "upper_bound")
    rules = PhysicalRules.complete_graph(cells, bound)
    menu = MenuSpecification.declare(quanta, max_group_size)
    initial = potential.reference
    declared_mass = Fraction(0)
    for value in initial:
        declared_mass += value
    return WorldConfiguration(
        study_id=study_id,
        configuration_id=configuration_id,
        potential=potential,
        rules=rules,
        menu=menu,
        initial_state=initial,
        declared_mass=declared_mass,
        arm=arm,
    )


def run_stage_a(
    configuration: WorldConfiguration,
    shocks: ShockSpecification,
    forcing_seed: int,
    actor_seed: int,
    horizon: int,
    budget: TickBudget | None = None,
) -> Run:
    """One shock at t = 0, then forcing OFF for every later tick.

    This advances model state. It is a transition execution class and produces
    no scientific claim by itself. Without an explicit budget the run is capped
    at the conformance ceiling, so a long study cannot start by accident.
    """
    if horizon < 1:
        raise Refusal("horizon must be at least one tick")
    run = Run(configuration, forcing_seed, actor_seed, budget or TickBudget.conformance())
    shock = draw_shock(configuration, shocks, forcing_seed)
    run.run_tick(forcing=shock)
    for _ in range(horizon - 1):
        run.run_tick(forcing=None)
    return run


def paired_arms(
    configuration: WorldConfiguration,
    shocks: ShockSpecification,
    forcing_seed: int,
    actor_seed: int,
    horizon: int,
    budget: TickBudget | None = None,
) -> dict[str, Run]:
    """Matched arms: EBU affordability versus the physical-random control.

    Both arms share the identical physical world, menu, feasibility rule,
    canonical ordering, forcing seed and actor seed. Because Stage A forces
    only at t = 0 from the identical initial state x*, the applied shock is
    provably identical in both arms -- common applied forcing, not merely
    common raw draws.

    The control is a scientific control, not an inferior controller.
    """
    return {
        ARM_EBU: run_stage_a(
            configuration.with_arm(ARM_EBU), shocks, forcing_seed, actor_seed, horizon, budget
        ),
        ARM_CONTROL: run_stage_a(
            configuration.with_arm(ARM_CONTROL), shocks, forcing_seed, actor_seed, horizon, budget
        ),
    }


def _rational(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def serialize_record(record: TickRecord) -> dict:
    """Deterministic, exactly replayable serialization of one tick."""
    return {
        "run_id": record.run_id,
        "configuration_id": record.configuration_id,
        "code_id": record.code_id,
        "arm": record.arm,
        "tick": record.tick,
        "state_before": [_rational(value) for value in record.state_before],
        "forcing": record.forcing,
        "forcing_rng_provenance": record.forcing_provenance,
        "state_frozen": [_rational(value) for value in record.state_frozen],
        "local_potential": [_rational(value) for value in record.local_potential],
        "audit_potential": _rational(record.audit_potential),
        "candidate_ids": list(record.candidate_ids),
        "feasible_ids": list(record.feasible_ids),
        "infeasible_reasons": [list(row) for row in record.infeasible_reasons],
        "ebu_values": [[gid, _rational(value)] for gid, value in record.ebu_values],
        "projected_balances": [
            [gid, [[owner, _rational(balance)] for owner, balance in rows]]
            for gid, rows in record.projected_balances
        ],
        "affordable_ids": list(record.affordable_ids),
        "chosen_id": record.chosen_id,
        "actor_rng_provenance": record.actor_provenance,
        "receipts": [[aid, _rational(value)] for aid, value in record.receipts],
        "state_after": [_rational(value) for value in record.state_after],
        "balances": [_rational(value) for value in record.balances],
        "balance_total": _rational(record.balance_total),
        "audit_ledger": _rational(record.audit_ledger),
        "conservation_residual": _rational(record.conservation_residual),
        "accounting_residual": _rational(record.accounting_residual),
        "nonnegativity_residual": _rational(record.nonnegativity_residual),
        "status": record.status,
    }


def serialize_run(run: Run) -> str:
    """Byte-stable JSON log. Every event is stored, never only a summary."""
    payload = {
        "protocol_id": STAGE_A_PROTOCOL_ID,
        "code_id": code_identity(),
        "study_id": run.configuration.study_id,
        "configuration_id": run.configuration.configuration_id,
        "arm": run.configuration.arm,
        "forcing_seed": run.forcing_seed,
        "actor_seed": run.actor_seed,
        "ticks": [serialize_record(record) for record in run.records],
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def deadlock_ticks(run: Run) -> tuple[int, ...]:
    """Ticks recorded as DEADLOCK. A scientific status, never a software fault."""
    return tuple(record.tick for record in run.records if record.status == STATUS_DEADLOCK)


def cycling_summary(run: Run) -> dict[str, object]:
    """Report (V, sum B) occupancy so exact-accounting cycling is visible.

    Cycling between (D, 0) and (0, D) is exact accounting with poor dynamics.
    It is logged rather than hidden and is not an implementation failure.
    """
    visited: dict[tuple[str, str], int] = {}
    for record in run.records:
        key = (_rational(record.audit_potential), _rational(record.balance_total))
        visited[key] = visited.get(key, 0) + 1
    revisited = {state: count for state, count in visited.items() if count > 1}
    return {
        "distinct_states": len(visited),
        "revisited_states": len(revisited),
        "max_revisits": max(visited.values()) if visited else 0,
    }
