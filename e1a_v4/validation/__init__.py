"""E1a v4 synthetic-validation package — PRE-EXECUTION. Nothing here has been run.

EXECUTION CLASS: NON-MODEL-ADVANCING in this stage. Every module below is written
so that the authorised execution stage can run it, but no module draws a random
number when imported, constructed or preflighted. The runner is required to
complete its entire preflight BEFORE it is handed an RNG, and that ordering is
tested with a sentinel provider that counts calls.

Two identities, deliberately separate (see plan.py):

    ANALYSIS PROCEDURE IDENTITY   e1a_v4.identity.procedure_identity
        binds the 12 analysis modules, the contract and the adopted rules.
        Calibration artifacts bind to THIS, as the bounded implementation requires.
        Adding this validation package does NOT change it.

    EXECUTION PROCEDURE IDENTITY  e1a_v4.validation.plan.execution_identity
        binds the analysis identity PLUS the validation module hashes, the
        validation plan and the seed map.
"""

from __future__ import annotations

VALIDATION_IDENTITY = "EBU-E1A-V4-SYNTHETIC-VALIDATION-v1"
SEED_DOMAIN = "EBU-E1A-V4-SYNTHETIC-VALIDATION"
CAMPAIGN_LABEL = "v4.0"
PLAN_MARKDOWN = "docs/e1a/E1A_V4_SYNTHETIC_VALIDATION_PLAN.md"
PLAN_JSON = "docs/e1a/e1a_v4_synthetic_validation_plan.json"
SEED_MAP_JSON = "docs/e1a/e1a_v4_seed_map.json"
