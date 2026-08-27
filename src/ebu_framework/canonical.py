"""EBU Canonical JSON Version 1 (ECJ-1).

Unicode assignment and NFC are derived exclusively from the two raw Unicode
15.0.0 assets shipped with this package.  No host text database, locale, ICU,
network source, or runtime download participates in canonical bytes.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import hashlib
import json
from pathlib import Path
import threading
from typing import NewType, TypeAlias

from .errors import FailureCode, _fail


ECJ1Value: TypeAlias = (
    dict[str, "ECJ1Value"]
    | list["ECJ1Value"]
    | str
    | int
    | bool
    | None
)
CanonicalBytes = NewType("CanonicalBytes", bytes)


class CanonicalizationVersion(StrEnum):
    ECJ1 = "ebu-canonical-json/1"


ECJ1_MEDIA_TYPE = 'application/json;profile="urn:ebu:canonical-json:1"'
UNICODE_VERSION = "15.0.0"
UNICODE_DATA_SHA256 = (
    "806e9aed65037197f1ec85e12be6e8cd870fc5608b4de0fffd990f689f376a73"
)
DERIVED_NORMALIZATION_PROPS_SHA256 = (
    "d5687a48c95c7d6e1ec59cb29c0f2e8b052018eb069a4371b7368d0561e12a29"
)

_UNICODE_ASSET_ROOT = (
    Path(__file__).resolve().parent / "data" / "unicode" / UNICODE_VERSION
)
_UNICODE_DATA_FILE = _UNICODE_ASSET_ROOT / "UnicodeData.txt"
_DERIVED_NORMALIZATION_PROPS_FILE = (
    _UNICODE_ASSET_ROOT / "DerivedNormalizationProps.txt"
)

_SBASE = 0xAC00
_LBASE = 0x1100
_VBASE = 0x1161
_TBASE = 0x11A7
_LCOUNT = 19
_VCOUNT = 21
_TCOUNT = 28
_NCOUNT = _VCOUNT * _TCOUNT
_SCOUNT = _LCOUNT * _NCOUNT


@dataclass(frozen=True, slots=True)
class _UnicodeTables:
    assigned: frozenset[int]
    combining_class: dict[int, int]
    canonical_decomposition: dict[int, tuple[int, ...]]
    composition: dict[tuple[int, int], int]


class _ObjectPairs(list[tuple[str, object]]):
    pass


_TABLE_LOCK = threading.Lock()
_TABLES: _UnicodeTables | None = None


def _read_verified_asset(path: Path, expected_sha256: str) -> bytes:
    try:
        before = path.lstat()
        if not path.is_file() or path.is_symlink():
            _fail(
                FailureCode.UNICODE_DATA_INTEGRITY_FAILURE,
                f"Unicode asset is not a regular non-symlink file: {path.name}",
            )
        data = path.read_bytes()
        after = path.lstat()
    except (OSError, ValueError) as exc:
        _fail(
            FailureCode.UNICODE_DATA_INTEGRITY_FAILURE,
            f"Unicode asset cannot be read: {path.name}: {exc}",
        )
    identity_before = (
        before.st_dev,
        before.st_ino,
        before.st_mode,
        before.st_size,
        before.st_mtime_ns,
    )
    identity_after = (
        after.st_dev,
        after.st_ino,
        after.st_mode,
        after.st_size,
        after.st_mtime_ns,
    )
    if identity_before != identity_after or len(data) != before.st_size:
        _fail(
            FailureCode.UNICODE_DATA_INTEGRITY_FAILURE,
            f"Unicode asset changed while being read: {path.name}",
        )
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected_sha256:
        _fail(
            FailureCode.UNICODE_DATA_INTEGRITY_FAILURE,
            f"Unicode asset digest mismatch: {path.name}",
        )
    return data


def _parse_full_composition_exclusions(data: bytes) -> frozenset[int]:
    exclusions: set[int] = set()
    try:
        text = data.decode("utf-8", "strict")
        for raw_line in text.splitlines():
            body = raw_line.split("#", 1)[0].strip()
            if not body:
                continue
            fields = [field.strip() for field in body.split(";")]
            if len(fields) < 2 or fields[1] != "Full_Composition_Exclusion":
                continue
            span = fields[0]
            if ".." in span:
                first_text, last_text = span.split("..", 1)
                first, last = int(first_text, 16), int(last_text, 16)
            else:
                first = last = int(span, 16)
            if first > last or first < 0 or last > 0x10FFFF:
                raise ValueError(f"invalid code-point span {span!r}")
            exclusions.update(range(first, last + 1))
    except (UnicodeDecodeError, ValueError) as exc:
        _fail(
            FailureCode.UNICODE_DATA_MALFORMED,
            f"DerivedNormalizationProps.txt is malformed: {exc}",
        )
    return frozenset(exclusions)


def _parse_unicode_data(
    data: bytes, exclusions: frozenset[int]
) -> _UnicodeTables:
    assigned: set[int] = set()
    combining: dict[int, int] = {}
    decompositions: dict[int, tuple[int, ...]] = {}
    pending_range: tuple[int, str, int, tuple[int, ...] | None] | None = None

    def add_entry(
        code_point: int,
        combining_class: int,
        decomposition: tuple[int, ...] | None,
    ) -> None:
        if 0xD800 <= code_point <= 0xDFFF:
            return
        if code_point in assigned:
            raise ValueError(f"duplicate code point U+{code_point:04X}")
        assigned.add(code_point)
        if combining_class:
            combining[code_point] = combining_class
        if decomposition:
            decompositions[code_point] = decomposition

    try:
        text = data.decode("utf-8", "strict")
        for line_number, line in enumerate(text.splitlines(), 1):
            fields = line.split(";")
            if len(fields) != 15:
                raise ValueError(f"line {line_number}: expected 15 fields")
            code_point = int(fields[0], 16)
            name = fields[1]
            combining_class = int(fields[3], 10)
            decomposition_field = fields[5].strip()
            decomposition: tuple[int, ...] | None = None
            if decomposition_field and not decomposition_field.startswith("<"):
                decomposition = tuple(
                    int(item, 16) for item in decomposition_field.split()
                )
            if name.endswith(", First>"):
                if pending_range is not None:
                    raise ValueError(f"line {line_number}: nested First range")
                pending_range = (
                    code_point,
                    name.removesuffix(", First>") + ">",
                    combining_class,
                    decomposition,
                )
                continue
            if name.endswith(", Last>"):
                if pending_range is None:
                    raise ValueError(f"line {line_number}: Last without First")
                first, expected_name, first_ccc, first_decomp = pending_range
                actual_name = name.removesuffix(", Last>") + ">"
                if actual_name != expected_name or code_point < first:
                    raise ValueError(f"line {line_number}: mismatched range")
                if combining_class != first_ccc or decomposition != first_decomp:
                    raise ValueError(f"line {line_number}: inconsistent range")
                for ranged_code_point in range(first, code_point + 1):
                    add_entry(ranged_code_point, first_ccc, first_decomp)
                pending_range = None
                continue
            if pending_range is not None:
                raise ValueError(f"line {line_number}: unterminated range")
            add_entry(code_point, combining_class, decomposition)
        if pending_range is not None:
            raise ValueError("unterminated final range")
    except (UnicodeDecodeError, ValueError) as exc:
        _fail(
            FailureCode.UNICODE_DATA_MALFORMED,
            f"UnicodeData.txt is malformed: {exc}",
        )

    composition: dict[tuple[int, int], int] = {}
    for composite, decomposition in decompositions.items():
        if len(decomposition) != 2 or composite in exclusions:
            continue
        key = (decomposition[0], decomposition[1])
        if key in composition and composition[key] != composite:
            _fail(
                FailureCode.UNICODE_DATA_MALFORMED,
                f"duplicate canonical composition for {key!r}",
            )
        composition[key] = composite
    return _UnicodeTables(
        assigned=frozenset(assigned),
        combining_class=combining,
        canonical_decomposition=decompositions,
        composition=composition,
    )


def _load_unicode_tables_from_paths(
    unicode_data_path: Path,
    derived_props_path: Path,
) -> _UnicodeTables:
    unicode_data = _read_verified_asset(
        unicode_data_path, UNICODE_DATA_SHA256
    )
    derived_props = _read_verified_asset(
        derived_props_path, DERIVED_NORMALIZATION_PROPS_SHA256
    )
    exclusions = _parse_full_composition_exclusions(derived_props)
    return _parse_unicode_data(unicode_data, exclusions)


def _unicode_tables() -> _UnicodeTables:
    global _TABLES
    if _TABLES is None:
        with _TABLE_LOCK:
            if _TABLES is None:
                _TABLES = _load_unicode_tables_from_paths(
                    _UNICODE_DATA_FILE,
                    _DERIVED_NORMALIZATION_PROPS_FILE,
                )
    return _TABLES


def _validate_scalar(code_point: int, tables: _UnicodeTables) -> None:
    if 0xD800 <= code_point <= 0xDFFF:
        _fail(
            FailureCode.INVALID_UNICODE_SCALAR,
            f"isolated surrogate U+{code_point:04X} is forbidden",
        )
    if code_point not in tables.assigned:
        _fail(
            FailureCode.UNASSIGNED_UNICODE_SCALAR,
            f"code point U+{code_point:04X} is unassigned in Unicode 15.0.0",
        )


def _hangul_decomposition(code_point: int) -> tuple[int, ...] | None:
    s_index = code_point - _SBASE
    if not 0 <= s_index < _SCOUNT:
        return None
    l = _LBASE + s_index // _NCOUNT
    v = _VBASE + (s_index % _NCOUNT) // _TCOUNT
    t_index = s_index % _TCOUNT
    if t_index:
        return (l, v, _TBASE + t_index)
    return (l, v)


def _decompose_scalar(
    code_point: int,
    tables: _UnicodeTables,
    output: list[int],
) -> None:
    hangul = _hangul_decomposition(code_point)
    if hangul is not None:
        output.extend(hangul)
        return
    decomposition = tables.canonical_decomposition.get(code_point)
    if decomposition is None:
        output.append(code_point)
        return
    for child in decomposition:
        _decompose_scalar(child, tables, output)


def _canonical_order(code_points: list[int], tables: _UnicodeTables) -> None:
    for index in range(1, len(code_points)):
        current_ccc = tables.combining_class.get(code_points[index], 0)
        if current_ccc == 0:
            continue
        cursor = index
        while cursor > 0:
            previous_ccc = tables.combining_class.get(
                code_points[cursor - 1], 0
            )
            if previous_ccc == 0 or previous_ccc <= current_ccc:
                break
            code_points[cursor - 1], code_points[cursor] = (
                code_points[cursor],
                code_points[cursor - 1],
            )
            cursor -= 1


def _hangul_composition(first: int, second: int) -> int | None:
    l_index = first - _LBASE
    if 0 <= l_index < _LCOUNT:
        v_index = second - _VBASE
        if 0 <= v_index < _VCOUNT:
            return _SBASE + (l_index * _VCOUNT + v_index) * _TCOUNT
    s_index = first - _SBASE
    if 0 <= s_index < _SCOUNT and s_index % _TCOUNT == 0:
        t_index = second - _TBASE
        if 0 < t_index < _TCOUNT:
            return first + t_index
    return None


def _compose_pair(
    first: int, second: int, tables: _UnicodeTables
) -> int | None:
    hangul = _hangul_composition(first, second)
    if hangul is not None:
        return hangul
    return tables.composition.get((first, second))


def _normalize_nfc(value: str) -> str:
    if type(value) is not str:
        _fail(
            FailureCode.ECJ1_TYPE_UNSUPPORTED,
            "NFC input must be an exact str",
        )
    tables = _unicode_tables()
    decomposed: list[int] = []
    for character in value:
        code_point = ord(character)
        _validate_scalar(code_point, tables)
        _decompose_scalar(code_point, tables, decomposed)
    _canonical_order(decomposed, tables)
    if not decomposed:
        return ""

    composed: list[int] = [decomposed[0]]
    starter_position = 0
    starter = decomposed[0]
    last_ccc = 0
    for code_point in decomposed[1:]:
        ccc = tables.combining_class.get(code_point, 0)
        composite = _compose_pair(starter, code_point, tables)
        if composite is not None and (last_ccc < ccc or last_ccc == 0):
            composed[starter_position] = composite
            starter = composite
            continue
        if ccc == 0:
            starter_position = len(composed)
            starter = code_point
        last_ccc = ccc
        composed.append(code_point)
    return "".join(chr(code_point) for code_point in composed)


def _project_value(value: object, active: set[int]) -> ECJ1Value:
    value_type = type(value)
    if value is None or value_type is bool or value_type is int:
        return value  # type: ignore[return-value]
    if value_type is float:
        _fail(FailureCode.FLOAT_FORBIDDEN, "Python float is forbidden in ECJ-1")
    if value_type is str:
        return _normalize_nfc(value)  # type: ignore[arg-type]
    if value_type is list:
        object_id = id(value)
        if object_id in active:
            _fail(FailureCode.CYCLIC_OBJECT_GRAPH, "cyclic ECJ-1 array")
        active.add(object_id)
        try:
            return [_project_value(item, active) for item in value]  # type: ignore[union-attr]
        finally:
            active.remove(object_id)
    if value_type is dict or value_type is _ObjectPairs:
        object_id = id(value)
        if object_id in active:
            _fail(FailureCode.CYCLIC_OBJECT_GRAPH, "cyclic ECJ-1 object")
        active.add(object_id)
        try:
            items = value.items() if value_type is dict else value  # type: ignore[union-attr]
            result: dict[str, ECJ1Value] = {}
            for original_key, item in items:
                if type(original_key) is not str:
                    _fail(
                        FailureCode.ECJ1_TYPE_UNSUPPORTED,
                        "ECJ-1 object names must be exact str values",
                    )
                key = _normalize_nfc(original_key)
                if key in result:
                    _fail(
                        FailureCode.DUPLICATE_OBJECT_NAME,
                        f"duplicate object name after NFC: {key!r}",
                    )
                result[key] = _project_value(item, active)
            return result
        finally:
            active.remove(object_id)
    _fail(
        FailureCode.ECJ1_TYPE_UNSUPPORTED,
        f"unsupported ECJ-1 value type: {value_type.__module__}.{value_type.__qualname__}",
    )


_SHORT_ESCAPES = {
    0x08: "\\b",
    0x09: "\\t",
    0x0A: "\\n",
    0x0C: "\\f",
    0x0D: "\\r",
}


def _encode_string(value: str) -> str:
    parts = ['"']
    for character in value:
        code_point = ord(character)
        if character == '"':
            parts.append('\\"')
        elif character == "\\":
            parts.append("\\\\")
        elif code_point in _SHORT_ESCAPES:
            parts.append(_SHORT_ESCAPES[code_point])
        elif code_point <= 0x1F:
            parts.append(f"\\u{code_point:04x}")
        else:
            parts.append(character)
    parts.append('"')
    return "".join(parts)


def _encode_projected(value: ECJ1Value) -> str:
    if value is None:
        return "null"
    if type(value) is bool:
        return "true" if value else "false"
    if type(value) is int:
        return str(value)
    if type(value) is str:
        return _encode_string(value)
    if type(value) is list:
        return "[" + ",".join(_encode_projected(item) for item in value) + "]"
    if type(value) is dict:
        keys = sorted(value)
        return "{" + ",".join(
            _encode_string(key) + ":" + _encode_projected(value[key])
            for key in keys
        ) + "}"
    _fail(FailureCode.CANONICALIZATION_FAILURE, "invalid projected ECJ-1 value")


def encode_ecj1(value: ECJ1Value) -> CanonicalBytes:
    """Project a strict ECJ-1 value and emit its unique UTF-8 bytes."""

    projected = _project_value(value, set())
    return CanonicalBytes(_encode_projected(projected).encode("utf-8"))


def _reject_raw_fraction_or_exponent(token: str) -> "NoReturn":
    _fail(
        FailureCode.INVALID_ECJ1,
        f"raw JSON fraction/exponent token is forbidden: {token!r}",
    )


def _reject_nonfinite(token: str) -> "NoReturn":
    _fail(FailureCode.INVALID_ECJ1, f"non-finite token is forbidden: {token!r}")


def parse_ecj1(data: bytes) -> ECJ1Value:
    """Strictly parse canonical ECJ-1 bytes and require byte-identical re-emit."""

    if type(data) is not bytes:
        _fail(FailureCode.INVALID_ECJ1, "ECJ-1 parser input must be exact bytes")
    try:
        text = data.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        _fail(FailureCode.INVALID_ECJ1, f"invalid UTF-8: {exc}")
    try:
        parsed = json.loads(
            text,
            object_pairs_hook=_ObjectPairs,
            parse_int=int,
            parse_float=_reject_raw_fraction_or_exponent,
            parse_constant=_reject_nonfinite,
        )
    except json.JSONDecodeError as exc:
        _fail(FailureCode.INVALID_ECJ1, f"invalid JSON syntax: {exc.msg}")
    projected = _project_value(parsed, set())
    emitted = encode_ecj1(projected)
    if bytes(emitted) != data:
        _fail(
            FailureCode.NONCANONICAL_ECJ1,
            "input bytes are valid JSON data but not canonical ECJ-1 bytes",
        )
    return projected


from typing import NoReturn  # noqa: E402


__all__ = (
    "CanonicalBytes",
    "CanonicalizationVersion",
    "ECJ1Value",
    "encode_ecj1",
    "parse_ecj1",
)
