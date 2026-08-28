"""Strict JSON and immutable identity helpers used by the Stage E harness."""

from __future__ import annotations

import hashlib
import json
import math
import unicodedata
from pathlib import Path
from typing import Any, Iterable
from itertools import permutations


class Refusal(RuntimeError):
    """Fail-closed rejection of an authority or conformance violation."""


def _pairs_no_duplicates(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise Refusal(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_float(value: str) -> None:
    raise Refusal(f"floating JSON number forbidden: {value}")


def _reject_constant(value: str) -> None:
    raise Refusal(f"non-finite JSON number forbidden: {value}")


def strict_loads(data: str | bytes, *, integers_only: bool = True) -> Any:
    """Parse JSON with duplicate, non-finite, and optionally float refusal."""

    if isinstance(data, bytes):
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise Refusal("JSON is not UTF-8") from exc
    else:
        text = data
    try:
        return json.loads(
            text,
            object_pairs_hook=_pairs_no_duplicates,
            parse_float=_reject_float if integers_only else float,
            parse_constant=_reject_constant,
        )
    except Refusal:
        raise
    except (json.JSONDecodeError, ValueError) as exc:
        raise Refusal(f"invalid JSON: {exc}") from exc


def strict_load(path: str | Path, *, integers_only: bool = True) -> Any:
    return strict_loads(Path(path).read_bytes(), integers_only=integers_only)


def _assert_json_value(value: Any) -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise Refusal("non-finite JSON value")
        raise Refusal("floating JSON value forbidden")
    if isinstance(value, list):
        for item in value:
            _assert_json_value(item)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise Refusal("JSON object key is not a string")
            _assert_json_value(item)
        return
    raise Refusal(f"non-JSON value: {type(value).__name__}")


def canonical_bytes(value: Any) -> bytes:
    """Return accepted canonical JSON: UTF-8, sorted, compact, no final LF."""

    _assert_json_value(value)
    text = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    text = unicodedata.normalize("NFC", text)
    return text.encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_digest(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def identity(kind: str, value: Any) -> dict[str, str]:
    digest = canonical_digest(value)
    return {"kind": kind, "value": digest, "sha256": digest}


def file_identity(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    data = file_path.read_bytes()
    return {
        "path": file_path.name,
        "byte_count": len(data),
        "sha256": sha256_bytes(data),
    }


def verify_identity(record: dict[str, Any], preimage: Any, *, kind: str | None = None) -> None:
    expected = canonical_digest(preimage)
    if kind is not None and record.get("kind") != kind:
        raise Refusal(f"identity kind mismatch: expected {kind}")
    if record.get("value") != expected or record.get("sha256") != expected:
        raise Refusal("identity digest mismatch")


def assert_text_integrity(data: bytes) -> None:
    if data.startswith(b"\xef\xbb\xbf"):
        raise Refusal("UTF-8 BOM forbidden")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise Refusal("text is not UTF-8") from exc
    if unicodedata.normalize("NFC", text) != text:
        raise Refusal("text is not NFC")
    if "\r" in text:
        raise Refusal("carriage return forbidden")
    if not text.endswith("\n") or text.endswith("\n\n"):
        raise Refusal("exactly one final LF required")
    for line in text.splitlines():
        if line != line.rstrip(" \t"):
            raise Refusal("trailing whitespace forbidden")


def canonical_topology_id(vertices: int, edges: Iterable[tuple[int, int]]) -> str:
    """Small exhaustive directed-graph oracle, deliberately limited to n<=8."""

    rows = list(edges)
    if not isinstance(vertices, int) or isinstance(vertices, bool) or not 0 <= vertices <= 8:
        raise Refusal("canonical topology oracle limited to 0..8 vertices")
    if len(rows) != len(set(rows)):
        raise Refusal("duplicate topology edge")
    if any(not (0 <= left < vertices and 0 <= right < vertices) for left, right in rows):
        raise Refusal("topology edge endpoint outside graph")
    best: bytes | None = None
    for permutation in permutations(range(vertices)):
        relabeled = sorted((permutation[left], permutation[right]) for left, right in rows)
        candidate = canonical_bytes({"vertices": vertices, "edges": [list(edge) for edge in relabeled]})
        if best is None or candidate < best:
            best = candidate
    if best is None:
        best = canonical_bytes({"vertices": 0, "edges": []})
    return sha256_bytes(best)
