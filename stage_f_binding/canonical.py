"""Outcome-blind canonical JSON and immutable Stage F identity helpers.

This module is deliberately standard-library-only.  It does not import the
project package, a runner, or any scientific implementation.
"""

from __future__ import annotations

import hashlib
import json
import math
import unicodedata
from pathlib import Path
from typing import Any, Iterable, Mapping


class BindingRefusal(RuntimeError):
    """Fail-closed rejection of malformed or inconsistent binding evidence."""


ZERO_SCIENCE_COUNTER_NAMES = (
    "model_execution_count",
    "trajectory_execution_count",
    "runner_import_count",
    "gate_execution_count",
    "transform_execution_count",
    "benchmark_execution_count",
    "simulation_execution_count",
    "stochastic_draw_count",
    "registered_configuration_count",
    "outcome_inspection_count",
    "result_count",
    "figure_count",
    "book_count",
    "release_action_count",
    "publication_action_count",
)

ZERO_SCIENCE_COUNTERS = {name: 0 for name in ZERO_SCIENCE_COUNTER_NAMES}


def _pairs_no_duplicates(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise BindingRefusal(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_float(value: str) -> None:
    raise BindingRefusal(f"floating JSON number forbidden: {value}")


def _reject_constant(value: str) -> None:
    raise BindingRefusal(f"non-finite JSON number forbidden: {value}")


def strict_loads(data: str | bytes, *, require_canonical: bool = False) -> Any:
    """Parse strict integer-only JSON, optionally requiring exact canonical bytes."""

    if isinstance(data, bytes):
        raw = data
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise BindingRefusal("JSON is not UTF-8") from exc
    elif isinstance(data, str):
        text = data
        try:
            raw = data.encode("utf-8")
        except UnicodeEncodeError as exc:
            raise BindingRefusal("JSON text cannot be encoded as UTF-8") from exc
    else:
        raise BindingRefusal("JSON input must be str or bytes")
    try:
        value = json.loads(
            text,
            object_pairs_hook=_pairs_no_duplicates,
            parse_float=_reject_float,
            parse_constant=_reject_constant,
        )
    except BindingRefusal:
        raise
    except (UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise BindingRefusal(f"invalid JSON: {exc}") from exc
    if require_canonical and raw != canonical_bytes(value):
        raise BindingRefusal("JSON bytes are not the exact canonical serialization")
    return value


def strict_load(path: str | Path, *, require_canonical: bool = False) -> Any:
    return strict_loads(Path(path).read_bytes(), require_canonical=require_canonical)


def _normalized_json(value: Any, *, path: str = "$") -> Any:
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise BindingRefusal(f"{path}: non-finite JSON value")
        raise BindingRefusal(f"{path}: floating JSON value forbidden")
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, list):
        return [_normalized_json(item, path=f"{path}[{index}]") for index, item in enumerate(value)]
    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise BindingRefusal(f"{path}: JSON object key is not a string")
            normalized_key = unicodedata.normalize("NFC", key)
            if normalized_key in normalized:
                raise BindingRefusal(f"{path}: NFC-normalized duplicate JSON key: {normalized_key}")
            normalized[normalized_key] = _normalized_json(item, path=f"{path}.{normalized_key}")
        return normalized
    raise BindingRefusal(f"{path}: non-JSON value: {type(value).__name__}")


def canonical_bytes(value: Any) -> bytes:
    """Return UTF-8 NFC, recursively key-sorted compact JSON with no final LF."""

    normalized = _normalized_json(value)
    try:
        return json.dumps(
            normalized,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except UnicodeEncodeError as exc:
        raise BindingRefusal("JSON value cannot be encoded as UTF-8") from exc


def canonical_text(value: Any) -> str:
    return canonical_bytes(value).decode("utf-8")


def sha256_hex(data: bytes) -> str:
    if not isinstance(data, bytes):
        raise BindingRefusal("SHA-256 input must be bytes")
    return hashlib.sha256(data).hexdigest()


def canonical_digest(value: Any) -> str:
    return sha256_hex(canonical_bytes(value))


def sha256_identity(kind: str, preimage: Any) -> dict[str, str]:
    """Build an identity over raw bytes or a canonical JSON preimage."""

    if not isinstance(kind, str) or not kind:
        raise BindingRefusal("identity kind must be a nonempty string")
    digest = sha256_hex(preimage) if isinstance(preimage, bytes) else canonical_digest(preimage)
    return {"kind": kind, "value": digest, "sha256": digest}


def verify_identity(
    record: Mapping[str, Any], preimage: Any, *, kind: str | None = None
) -> None:
    if not isinstance(record, Mapping) or set(record) != {"kind", "value", "sha256"}:
        raise BindingRefusal("identity must contain exactly kind, value, and sha256")
    if not isinstance(record["kind"], str) or not record["kind"]:
        raise BindingRefusal("identity kind must be a nonempty string")
    if kind is not None and record["kind"] != kind:
        raise BindingRefusal(f"identity kind mismatch: expected {kind}")
    digest = sha256_hex(preimage) if isinstance(preimage, bytes) else canonical_digest(preimage)
    if record["value"] != digest or record["sha256"] != digest:
        raise BindingRefusal("identity value/sha256/canonical-preimage mismatch")


def verify_embedded_digest(
    record: Mapping[str, Any], digest_field: str, *, kind: str | None = None
) -> dict[str, str]:
    """Verify a record digest whose sole omission is ``digest_field``.

    The returned identity uses the record-schema kind supplied by authority.
    """

    if not isinstance(record, Mapping) or digest_field not in record:
        raise BindingRefusal(f"embedded digest field missing: {digest_field}")
    if not isinstance(record[digest_field], str):
        raise BindingRefusal(f"embedded digest is not a string: {digest_field}")
    preimage = {key: value for key, value in record.items() if key != digest_field}
    digest = canonical_digest(preimage)
    if record[digest_field] != digest:
        raise BindingRefusal(f"embedded digest mismatch: {digest_field}")
    if kind is None:
        kind = record.get("schema") if isinstance(record.get("schema"), str) else ""
    if not kind:
        raise BindingRefusal("embedded-digest identity kind is missing")
    return {"kind": kind, "value": digest, "sha256": digest}


def assert_zero_science_counters(counters: Mapping[str, Any]) -> None:
    if not isinstance(counters, Mapping) or dict(counters) != ZERO_SCIENCE_COUNTERS:
        raise BindingRefusal("scientific counters are not the exact closed all-zero set")


__all__ = (
    "BindingRefusal",
    "ZERO_SCIENCE_COUNTER_NAMES",
    "ZERO_SCIENCE_COUNTERS",
    "assert_zero_science_counters",
    "canonical_bytes",
    "canonical_digest",
    "canonical_text",
    "sha256_hex",
    "sha256_identity",
    "strict_load",
    "strict_loads",
    "verify_embedded_digest",
    "verify_identity",
)
