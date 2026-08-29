"""Outcome-blind Stage E scientific-harness conformance package.

This private package deliberately contains no project runner and exposes no
registered-study execution route.  It exists only to verify the authorities,
identities, schemas, exact algorithms, continuation mechanics, and resource
boundaries required before Stage F.
"""

from .canonical import Refusal, canonical_bytes, canonical_digest, identity

__all__ = ["Refusal", "canonical_bytes", "canonical_digest", "identity"]

__version__ = "1.0.0-stage-e"
