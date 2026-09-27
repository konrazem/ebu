"""Structured analysis status. Fail-closed by construction.

A status is never NaN and never a bare bool: downstream endpoints branch on the
status, so an unusable result must be *nameable*. Historical crash paths that
read `beta_hat` unconditionally cannot survive this type, because a result
without `ESTIMATED` carries no `beta_hat` at all.
"""

from __future__ import annotations

from enum import Enum


class AnalysisStatus(str, Enum):
    ESTIMATED = "ESTIMATED"
    BRANCH_A_INVALID = "BRANCH_A_INVALID"
    NON_POSITIVE_DEFINITE = "NON_POSITIVE_DEFINITE"
    RANK_GUARD_FAIL = "RANK_GUARD_FAIL"
    N_EFF_UNSUPPORTED = "N_EFF_UNSUPPORTED"
    MODE_UNRESOLVED = "MODE_UNRESOLVED"
    CALIBRATION_MISSING = "CALIBRATION_MISSING"
    CALIBRATION_IDENTITY_MISMATCH = "CALIBRATION_IDENTITY_MISMATCH"
    GEOMETRY_FAIL = "GEOMETRY_FAIL"
    ANALYSIS_INVALID = "ANALYSIS_INVALID"

    @property
    def is_estimated(self) -> bool:
        return self is AnalysisStatus.ESTIMATED


#: Statuses that make every downstream endpoint fail closed.
NON_ESTIMATED = frozenset(s for s in AnalysisStatus if s is not AnalysisStatus.ESTIMATED)
