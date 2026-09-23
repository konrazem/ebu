"""One-shock recovery trials under the corrected termination semantics.

Mission section 10, and `STAGE_A_RECOVERY_INTERPRETATION_CORRECTION.md`.

Protocol, frozen:

    1. begin at the reference, V = 0, B = 0, J = 0
    2. apply one declared conservative shock, actor not invited
    3. external forcing OFF for the remainder of the trial
    4. mandatory actions continue -- the actor must act every tick
    5. terminate at the FIRST tick with V = 0: this is a successful recovery
    6. otherwise NOT_RECOVERED_WITHIN_HORIZON at the frozen horizon

The trial does **not** continue past the first hit. Continuing it and then
counting later mandatory actions as a recovery failure is exactly the
conflation the correction note removes: those later actions belong to the
continued-demand question, which the homeostasis study measures separately with
occupancy rather than with `V = 0`.

This measures the ability to recover from a *finite* disturbance. It measures
nothing about persistent-demand homeostasis.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from gaussian_harness.forcing import ForcingIncrement
from gaussian_harness.harness import TickBudget
from gaussian_harness.numerics import Refusal

from .harness import PolicyRun, PolicyWorld

RECOVERY_PROTOCOL_ID = "EBU-GAUSSIAN-ONE-SHOCK-RECOVERY-v2"

OUTCOME_RECOVERED = "RECOVERED"
OUTCOME_NOT_RECOVERED = "NOT_RECOVERED_WITHIN_HORIZON"


@dataclass(frozen=True)
class RecoveryOutcome:
    """Result of one recovery trial. `first_hit` is 1-indexed in actor ticks."""

    policy: str
    outcome: str
    first_hit: int | None
    horizon: int
    disturbance: Fraction
    ticks_used: int
    peak_radial_square: Fraction
    max_accounting_residual: Fraction

    @property
    def recovered(self) -> bool:
        return self.outcome == OUTCOME_RECOVERED


def recovery_trial(
    world: PolicyWorld,
    shock: ForcingIncrement,
    forcing_seed: int,
    actor_seed: int,
    horizon: int,
    budget: TickBudget | None = None,
) -> RecoveryOutcome:
    """Run one trial, stopping at the first tick with `V = 0`."""
    if horizon < 1:
        raise Refusal("recovery horizon must be at least one actor tick")
    if world.initial_state != world.potential.reference:
        raise Refusal("a recovery trial must begin exactly at the reference")

    run = PolicyRun(world, forcing_seed, actor_seed, budget or TickBudget.conformance())
    opening = run.run_tick(shock=shock, actor_enabled=False)
    disturbance = opening.potential_total
    if disturbance <= 0:
        raise Refusal("the declared shock did not move the system off the reference")

    peak = opening.radial_square
    worst = abs(opening.accounting_residual)
    for step in range(1, horizon + 1):
        record = run.run_tick(load=None)
        peak = max(peak, record.radial_square)
        worst = max(worst, abs(record.accounting_residual))
        if record.potential_total == 0:
            # First hit terminates the trial successfully. Nothing after this
            # tick is executed, observed or counted.
            return RecoveryOutcome(
                world.policy, OUTCOME_RECOVERED, step, horizon, disturbance,
                run.tick, peak, worst,
            )
    return RecoveryOutcome(
        world.policy, OUTCOME_NOT_RECOVERED, None, horizon, disturbance,
        run.tick, peak, worst,
    )
