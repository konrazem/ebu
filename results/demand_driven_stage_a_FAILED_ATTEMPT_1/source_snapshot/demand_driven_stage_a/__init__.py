"""Registered execution tooling for `EBU-DEMAND-DRIVEN-STAGE-A-v1`.

This package is **not** the mechanism. It constructs the declared episodes,
applies the frozen stopping and reporting rules of
`DEMAND_DRIVEN_STAGE_A_PREREGISTRATION.md`, and writes artifacts. It lives
outside `demand_driven_ebu` on purpose: the preregistration pins that package's
identity, so registration-time tooling must not perturb it.

It is a different study from the root `stage_a_execute.py` / `stage_a_registry.py`,
which implement `EBU-STAGE-A-V1` over `gaussian_harness`. Neither is executed,
imported or repurposed here.
"""

REGISTRATION_ID = "EBU-DEMAND-DRIVEN-STAGE-A-v1"

__all__ = ["REGISTRATION_ID"]
