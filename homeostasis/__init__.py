"""Gaussian homeostasis mission: reference region, actor policies and metrics.

This package answers a different question from Stage A and Stage B. Those asked
whether the physical state returns to, or stays at, the exact reference. This
one asks whether the physical state stays statistically *localized around* the
reference under continuing disturbance and mandatory action, and how that
changes with the actor's policy.

`gaussian_harness` is imported and never modified: its code identity
`a9158eef...` is pinned by the registered Stage-A and Stage-B artifacts, and a
single byte changed there would invalidate their replay. Everything new lives
here, in a package with its own identity.

Homeostasis is a property of the physical state only. No balance, capacity,
receipt, settlement or audit-ledger quantity appears in any metric defined
here (mission section 4).
"""

from __future__ import annotations

MISSION_ID = "EBU-GAUSSIAN-HOMEOSTASIS-MISSION-v1"
