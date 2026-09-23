"""The frozen stop conditions, as pure functions of one recorded transition.

Separated from the runner so that the precedence rules can be checked on
SYNTHETIC records without executing anything. Nothing here imports a run,
constructs a world, or advances a state.

Section 2 (A1) and section 4 (A3) of the preregistration.
"""

from __future__ import annotations

from demand_driven_ebu.harness import STATUS_ALL_UNAFFORDABLE

RETURNED_TO_REFERENCE = "RETURNED_TO_REFERENCE"
NO_AFFORDABLE_SOLUTION = "NO_AFFORDABLE_SOLUTION"
HORIZON_REACHED = "HORIZON_REACHED"

A1_STOPPING_REASONS = (
    RETURNED_TO_REFERENCE,
    NO_AFFORDABLE_SOLUTION,
    HORIZON_REACHED,
)
A3_STOPPING_REASONS = (HORIZON_REACHED,)


def a1_stop(
    *, state_after, reference, epoch_status: str, epoch: int, horizon: int
) -> str | None:
    """A1's stop rule, evaluated after the transition of epoch `epoch`.

    The conditions are NOT mutually exclusive, so the declared order S1, S2, S3
    is applied literally and the first that holds wins. On the final permitted
    transition `epoch + 1 == horizon` a return or an unaffordable stall
    therefore outranks the horizon, and `HORIZON_REACHED` is recorded only when
    the horizon is genuinely the first condition to hold.
    """
    if tuple(state_after) == tuple(reference):        # S1
        return RETURNED_TO_REFERENCE
    if epoch_status == STATUS_ALL_UNAFFORDABLE:       # S2
        return NO_AFFORDABLE_SOLUTION
    if epoch + 1 == horizon:                          # S3
        return HORIZON_REACHED
    return None


def a2_stop(*, epoch: int, horizon: int) -> str | None:
    """A2 is a single-epoch episode: the horizon is the only stop."""
    if epoch + 1 == horizon:
        return HORIZON_REACHED
    return None


def a3_stop(*, epoch: int, horizon: int) -> str | None:
    """A3's stop rule. It deliberately does NOT inherit A1's S1.

    A3's order arrives at epoch 3. An episode that stopped on reaching the
    reference would terminate during the prelude and never observe the event
    the class exists for. Reaching `x*` early is an ordinary recorded event,
    and the horizon is the only ordinary terminal condition -- so the
    post-arrival observation window is the same length in every arm.
    """
    if epoch + 1 == horizon:
        return HORIZON_REACHED
    return None


STOP_RULES = {"A1": a1_stop, "A2": a2_stop, "A3": a3_stop}
