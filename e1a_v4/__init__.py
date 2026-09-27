"""E1a v4 — bounded implementation of the adopted prospective design.

The authoritative sources for every decision rule are

    docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md
    docs/e1a/e1a_v4_design_contract.json

and this package **reads them**. No adopted constant is typed into code here: if
the contract and an implementation disagree, THE DESIGN WINS and the mismatch is
a fail-closed refusal.

Scientific target, unchanged:

    K_theta = beta H_theta        one field-independent beta over four fields
    V_theta(x) = [U_theta(x) - U_theta(x*_theta)] / (k_B T_theta)
    H_theta    = H_U,theta / (k_B T_theta)
    prediction: beta = 1 at every tested field, BENCHMARK-SPECIFIC

beta is estimated from the independent measurement branches and is never forced
to equal the prediction.

EXECUTION CLASS: NON-MODEL-ADVANCING. Nothing in this package draws a random
number, generates an initial state, produces a trajectory or steps an OU
process. The stochastic synthetic-validation campaign is a separate authorised
stage and has not begun.

Relation to existing packages: `gaussian_harness`, `capacity_v2`,
`demand_driven_ebu` and `homeostasis` are separate registered model paths. None
is imported, modified or reinterpreted here. There is no prior E1a code in the
repository - the v1-v3 gate packages were never committed - so this is the first
E1a implementation, not a parallel second framework.
"""

from __future__ import annotations

IMPLEMENTATION_IDENTITY = "EBU-E1A-V4-IMPLEMENTATION-v1"
DESIGN_DOCUMENT = "docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md"
DESIGN_CONTRACT = "docs/e1a/e1a_v4_design_contract.json"
FROZEN_FOUNDATION = "docs/physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md"
WORKING_BASELINE = "docs/theory/EBU_THEORY_BASELINE.md"

K_B = 1.380649e-23  # J/K, SI defining constant
