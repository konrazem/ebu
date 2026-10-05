"""E1a V-stage candidate reference implementation (direct-bridge, v5).

NON-CONTROLLING CANDIDATE.  This package is an isolated prospective
implementation of the independently cleared T-stage minimal equilibrium
experiment design and U-stage Branch-A calibration specification.  It does
not modify, supersede or reuse the paused ``e1a_v4`` operational identities.

Scope boundaries, fixed by the authorising V-stage brief:

* synthetic pre-execution validation only;
* no physical experiment, no real calibration data, no official campaign;
* no execution authorisation is conferred by anything in this package.

Sign convention (T-stage section 5, ordinary post-minus-pre)::

    E_EBU      = V(x_pre) - V(x_post)
    delta_J    = J_post - J_pre = -E_EBU

The ambiguous bare symbol ``Delta J`` is never used in this package; the
baseline section 14.3 documentary sign defect is recorded as still owed before
W-stage authority freeze and is NOT repaired here.
"""

CANDIDATE_STATUS = "NON-CONTROLLING CANDIDATE"
POLICY_VERSION = "E1A-T11a-RF-v1"
EXECUTION_AUTHORISED = False

__all__ = ["CANDIDATE_STATUS", "POLICY_VERSION", "EXECUTION_AUTHORISED"]
