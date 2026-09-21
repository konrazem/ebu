"""Demand-driven EBU economy: a new prospective model path.

The controlling correction this package implements is that an actor does not
choose among all physically possible transfers. It chooses only among physical
plans that actually serve a currently existing demand:

    demand -> demand-serving plans -> can this plan actually happen now?
    -> exact EBU valuation -> affordability -> actor choice -> execution

Two demand sources coexist. `P` is physical/homeostatic demand, read directly
off the physical state and never stored in a queue. `E` is exogenous economic
demand, which arrives from outside, may exceed what physically exists, and is
admitted by an EBU-blind random policy. There is no FIFO queue, no scheduler
and no EBU-based demand priority anywhere in this package.

This package is deliberately isolated. It does not modify, import state from,
or re-register `gaussian_harness` or `capacity_v2`, whose registered code
identities are pinned by historical preregistrations. It reuses only pure,
stateless mathematics from `gaussian_harness` (the exact rational numeric
policy, and the Level-1 Gaussian potential as a cross-check oracle), which
changes no byte of those packages.

Nothing here is registered, preregistered or frozen. Building this model is not
evidence about it.
"""

from __future__ import annotations

MODEL_ID = "EBU-DEMAND-DRIVEN-ECONOMY-v1"
CONTRACT_REF = "DEMAND_DRIVEN_EBU_SCIENTIFIC_CONTRACT.md"

__all__ = ["MODEL_ID", "CONTRACT_REF"]
