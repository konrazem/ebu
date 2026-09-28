"""Strict JSON parsing for AUTHORITATIVE documents. Duplicate keys REFUSE.

THE DEFECT THIS CLOSES
    `json.loads` resolves a duplicate object key by silently keeping the LAST
    occurrence. A human reading the document top-to-bottom sees the FIRST. So

        {"plan_version": "0.0.1-TAMPERED",
         "plan_version": "1.7.0"}

    parses to the correct value while every human reader sees the tampered one,
    and nothing refuses. Reproduced against this package at the previous HEAD, in
    the generated authority block, inside a nested case record, and in the
    authoritative plan JSON itself: all three were ACCEPTED.

    Choosing "first wins" instead would be no better. An authoritative document
    that says two things is AMBIGUOUS, and the only safe resolution is refusal.

HOW
    `json.load(..., object_pairs_hook=...)` invokes the hook for EVERY object,
    innermost first, with the pairs in document order and duplicates preserved.
    Detecting a repeat in that list therefore catches duplicates at any depth,
    including inside a case or subcondition record.

CLASSIFICATION
    duplicate detection ... EXACT (deterministic over the parsed token stream)

NO RNG. Nothing in this module draws or advances any model state.
"""

from __future__ import annotations

import json
import os
from typing import Any

from .refusals import PlanDuplicateKey, PlanStructureInvalid


def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """`object_pairs_hook`. Called for every object at every depth."""
    seen: dict[str, Any] = {}
    for key, value in pairs:
        if key in seen:
            raise PlanDuplicateKey(
                f"duplicate object key {key!r}. An authoritative document that "
                "states a key twice is AMBIGUOUS: a reader sees the first value "
                "and an ordinary parser keeps the last. Neither is adopted."
            )
        seen[key] = value
    return seen


def strict_loads(text: str, what: str) -> Any:
    """Parse authoritative JSON text. Duplicate keys at ANY depth refuse."""
    try:
        return json.loads(text, object_pairs_hook=_reject_duplicates)
    except PlanDuplicateKey as exc:
        raise PlanDuplicateKey(f"{what}: {exc.message}") from None
    except json.JSONDecodeError as exc:
        raise PlanStructureInvalid(f"{what} is not valid JSON: {exc}") from exc


def strict_load_file(path: str, what: str) -> Any:
    """Read and strictly parse an authoritative JSON file."""
    if not os.path.exists(path):
        raise PlanStructureInvalid(f"{what} is absent: {path}")
    with open(path, encoding="utf-8") as handle:
        return strict_loads(handle.read(), what)
