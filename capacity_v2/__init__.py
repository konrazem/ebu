"""Capacity V2 candidate: deviation-bounded local capacity (DBLC).

A SEPARATE experimental model path. The registered Stage-A and Stage-B
mechanism lives in `gaussian_harness` and is not modified, imported-over or
reinterpreted by anything here; that package's code identity must stay
`a9158eef...` so both registered studies remain byte-reproducible.

Rule (see CAPACITY_V2_CANDIDATE_ANALYSIS.md section 3):

    affordability:  B_i + Delta B_i >= 0          (unchanged from V1)
    settlement:     B_i^raw = B_i + Delta B_i
    ceiling:        B_i'    = min(B_i^raw, V_i(x'))
    retirement:     C      += sum_i (B_i^raw - B_i')
    invariant:      B_i <= V_i(x_i) at every observation point
    exact ledger:   V + sum_i B_i + C = J

A cell's licence to damage is limited by the deviation it is currently
carrying. Once a cell is back at its reference its claim is settled and void.

EBU still calculates and actors still choose. Nothing here ranks actions.
"""

from __future__ import annotations

MODEL_IDENTITY = "EBU-CAPACITY-V2-DEVIATION-BOUNDED-LOCAL-v1"
HISTORICAL_MODEL_IDENTITY = "EBU-CAPACITY-V1-PERSISTENT-ABSOLUTE-v1"
