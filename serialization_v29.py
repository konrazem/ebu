"""
V2.9 Gate 2.4B - strict fail-closed result serialization + the narrowly scoped
aggregate-diagnostic normalization.

Motivation (audit trail): the Attempt-2 D9/D10 study produced non-finite
`stability_tau`/`stability_amp` aggregate diagnostics on diverging D10 runs;
`json.dump` with the stdlib default `allow_nan=True` would have serialized them
as the non-standard JSON tokens `Infinity`/`NaN`. The committed summary was
repaired post hoc (Gate 2.4A authorization, no regeneration; see
results/v2.9/d9_d10/ATTEMPT_2_SERIALIZATION_REPAIR.md). This module makes any
FUTURE result write fail closed instead:

  * strict_dumps / strict_dump serialize with allow_nan=False - an unexpected
    non-finite float anywhere in the payload raises instead of emitting
    non-standard JSON;
  * normalize_aggregate_diagnostics() is the ONLY sanctioned normalization:
    it converts non-finite values of the two explicitly nullable AGGREGATE
    DIAGNOSTICS (`stability_tau`, `stability_amp`) to None BEFORE serialization
    and records an explicit machine-readable reason on the record; a non-finite
    value in ANY other field (states, flows, service, unmet demand, crossings,
    classifications, physical over-use, ledger values, timestep/certificate
    data, ...) raises NonFiniteFieldError - it is never silently converted.

No physical update law, policy, classifier, tolerance, or plan value lives in
or is altered by this module; it acts only on completed records at the
serialization boundary. Standard library only; import-safe.
"""
from __future__ import annotations
import json
import math

# The ONLY aggregate fields that may be non-finite at aggregation time and are
# normalized to JSON null (each with a recorded reason). Both are researcher
# stability DIAGNOSTICS (Amendment 1 Sec 17.4), never decision-path inputs and
# never scientific classifications. Every other field fails closed.
NULLABLE_DIAGNOSTICS = ("stability_tau", "stability_amp")

# Machine-readable normalization reasons.
REASON_OVERFLOW = "overflow_on_diverging_trajectory"
REASON_UNDEFINED_EXIT = "undefined_after_domain_exit"
REASON_UNDEFINED_WINDOW = "undefined_insufficient_postburn_window"

# Key added to a normalized aggregate record: {field_name: reason}.
NORMALIZATION_KEY = "diagnostic_normalizations"


class NonFiniteFieldError(ValueError):
    """A field whose schema requires finiteness holds NaN or +/-Infinity."""


def _nonfinite_paths(obj, path):
    """Yield JSON-ish paths of every non-finite float inside obj."""
    if isinstance(obj, float):
        if not math.isfinite(obj):
            yield path or "<root>"
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from _nonfinite_paths(v, f"{path}.{k}" if path else str(k))
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            yield from _nonfinite_paths(v, f"{path}[{i}]")


def assert_all_finite(obj, label: str = "") -> None:
    """Hard validation: raise NonFiniteFieldError if any float in obj is
    non-finite. Used for trace records and full summaries, where NO field is
    nullable-by-overflow."""
    bad = list(_nonfinite_paths(obj, label))
    if bad:
        raise NonFiniteFieldError(
            "non-finite value in field(s) requiring finiteness: "
            + ", ".join(bad[:10])
            + ("" if len(bad) <= 10 else f" (+{len(bad) - 10} more)"))


def normalize_aggregate_diagnostics(agg: dict) -> dict:
    """Narrow deterministic normalization of ONE completed aggregate record.

    - `stability_tau`/`stability_amp`: a non-finite value becomes None with
      reason REASON_OVERFLOW; an already-None value (the frozen classifier
      returns (\"unclassified\", None, None) when the post-burn-in window has
      fewer than 4 valid samples) gets its reason annotated but is not changed.
    - Already-finite values (diagnostics included) are never altered.
    - A non-finite float in ANY other field raises NonFiniteFieldError: states,
      flows, service, unmet demand, crossings, classifications, O_physical,
      ledger values, and timestep/certificate data are never normalized.

    Mutates and returns agg. Adds NORMALIZATION_KEY only when at least one
    diagnostic is null after normalization."""
    reasons = {}
    for field in NULLABLE_DIAGNOSTICS:
        if field not in agg:
            raise NonFiniteFieldError(
                f"aggregate record lacks required diagnostic field '{field}'")
        v = agg[field]
        if v is None:
            reasons[field] = (REASON_UNDEFINED_EXIT
                              if agg.get("terminal_status") == "domain_exit"
                              else REASON_UNDEFINED_WINDOW)
        elif isinstance(v, float) and not math.isfinite(v):
            agg[field] = None
            reasons[field] = REASON_OVERFLOW
        # finite values pass through untouched
    rest = {k: v for k, v in agg.items() if k not in NULLABLE_DIAGNOSTICS}
    assert_all_finite(rest, "aggregate")
    if reasons:
        agg[NORMALIZATION_KEY] = reasons
    return agg


def strict_dumps(obj, **kwargs) -> str:
    """json.dumps that fails closed: allow_nan=False is forced (a caller
    cannot re-enable non-standard tokens through kwargs)."""
    kwargs.pop("allow_nan", None)
    return json.dumps(obj, allow_nan=False, **kwargs)


def strict_dump(obj, fh, **kwargs) -> None:
    """json.dump that fails closed: allow_nan=False is forced."""
    kwargs.pop("allow_nan", None)
    json.dump(obj, fh, allow_nan=False, **kwargs)
