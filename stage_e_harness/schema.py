"""Fail-closed validator for the exact Draft 2020-12 subset frozen by Stage E.

The implementation intentionally supports only the vocabulary derived from the
three accepted controlling schemas.  Unsupported assertions never degrade to
annotations or permissive success.
"""

from __future__ import annotations

import re
from copy import deepcopy
from typing import Any, Iterable

from .canonical import Refusal, canonical_bytes


SUPPORTED_KEYWORDS = (
    "$defs",
    "$id",
    "$ref",
    "$schema",
    "additionalProperties",
    "allOf",
    "const",
    "description",
    "else",
    "enum",
    "format",
    "if",
    "items",
    "maxItems",
    "maximum",
    "minItems",
    "minLength",
    "minProperties",
    "minimum",
    "oneOf",
    "pattern",
    "prefixItems",
    "properties",
    "required",
    "then",
    "title",
    "type",
    "uniqueItems",
)

AUTHORITY_METADATA_KEYS = (
    "accepted_stage_d_schema",
    "completion_marker",
    "prospective_instance_count",
    "prospective_negative_schema_cases",
    "prospective_negative_validation_cases",
    "prospective_non_evidence_schema_fixtures",
    "schema_version",
    "scientific_execution_count",
    "stage_d_instance_count",
    "stage_e_instance_count",
    "verbatim_user_mobius_topology_controls",
)

ASSERTION_APPLICATOR_MUTATIONS = (
    "$ref",
    "additionalProperties",
    "allOf",
    "const",
    "else",
    "enum",
    "if",
    "items",
    "maxItems",
    "maximum",
    "minItems",
    "minLength",
    "minProperties",
    "minimum",
    "oneOf",
    "pattern",
    "prefixItems",
    "properties",
    "required",
    "then",
    "type",
    "uniqueItems",
)


def _same(left: Any, right: Any) -> bool:
    """JSON equality without Python's bool/int aliasing."""

    if type(left) is not type(right):
        return False
    if isinstance(left, list):
        return len(left) == len(right) and all(_same(a, b) for a, b in zip(left, right))
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(_same(left[key], right[key]) for key in left)
    return bool(left == right)


def _is_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _matches_type(value: Any, type_name: str) -> bool:
    return {
        "null": value is None,
        "boolean": isinstance(value, bool),
        "integer": _is_integer(value),
        "number": (_is_integer(value) or (isinstance(value, float) and not isinstance(value, bool))),
        "string": isinstance(value, str),
        "array": isinstance(value, list),
        "object": isinstance(value, dict),
    }.get(type_name, False)


def _resolve_pointer(root: Any, reference: str) -> Any:
    if not reference.startswith("#/"):
        raise Refusal(f"only local schema references are supported: {reference}")
    value = root
    for raw in reference[2:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(value, list):
            try:
                value = value[int(token)]
            except (ValueError, IndexError) as exc:
                raise Refusal(f"unresolved local schema reference: {reference}") from exc
        elif isinstance(value, dict) and token in value:
            value = value[token]
        else:
            raise Refusal(f"unresolved local schema reference: {reference}")
    return value


def _schema_children(key: str, value: Any) -> Iterable[Any]:
    if key in {"$defs", "properties"}:
        if not isinstance(value, dict):
            raise Refusal(f"{key} must be an object")
        return value.values()
    if key in {"allOf", "oneOf", "prefixItems"}:
        if not isinstance(value, list):
            raise Refusal(f"{key} must be an array")
        return value
    if key in {"additionalProperties", "items", "if", "then", "else"} and isinstance(value, dict):
        return (value,)
    return ()


def audit_schema_vocabulary(schema: dict[str, Any], *, allowed_metadata: Iterable[str]) -> tuple[str, ...]:
    allowed_metadata_set = set(allowed_metadata)
    seen: set[str] = set()

    def visit(node: Any, *, root: bool = False) -> None:
        if isinstance(node, bool):
            return
        if not isinstance(node, dict):
            raise Refusal("schema node must be an object or boolean")
        for key, value in node.items():
            if key in SUPPORTED_KEYWORDS:
                seen.add(key)
                for child in _schema_children(key, value):
                    visit(child)
            elif root and key in allowed_metadata_set:
                continue
            else:
                raise Refusal(f"unsupported schema keyword or metadata key: {key}")

    visit(schema, root=True)
    return tuple(key for key in SUPPORTED_KEYWORDS if key in seen)


class Validator:
    """Exact closed-subset schema validator."""

    def __init__(self, schema: dict[str, Any], *, allowed_metadata: Iterable[str] = ()) -> None:
        self.schema = schema
        self.vocabulary = audit_schema_vocabulary(schema, allowed_metadata=allowed_metadata)

    def validate(self, instance: Any, schema: Any | None = None, *, path: str = "$") -> None:
        target = self.schema if schema is None else schema
        self._validate(instance, target, path)

    def is_valid(self, instance: Any, schema: Any | None = None) -> bool:
        try:
            self.validate(instance, schema)
        except Refusal:
            return False
        return True

    def definition(self, name: str) -> dict[str, Any]:
        definitions = self.schema.get("$defs", {})
        if name not in definitions:
            raise Refusal(f"unknown schema definition: {name}")
        return definitions[name]

    def validate_definition(self, name: str, instance: Any) -> None:
        self.validate(instance, self.definition(name), path=f"$defs.{name}")

    def _validate(self, instance: Any, schema: Any, path: str) -> None:
        if schema is True:
            return
        if schema is False:
            raise Refusal(f"{path}: false schema")
        if not isinstance(schema, dict):
            raise Refusal(f"{path}: malformed schema node")

        reference = schema.get("$ref")
        if reference is not None:
            if not isinstance(reference, str):
                raise Refusal(f"{path}: non-string $ref")
            self._validate(instance, _resolve_pointer(self.schema, reference), path)

        if "type" in schema:
            required_types = schema["type"]
            if isinstance(required_types, str):
                required_types = [required_types]
            if not isinstance(required_types, list) or not required_types or not all(isinstance(item, str) for item in required_types):
                raise Refusal(f"{path}: malformed type")
            if not any(_matches_type(instance, item) for item in required_types):
                raise Refusal(f"{path}: type mismatch")

        if "const" in schema and not _same(instance, schema["const"]):
            raise Refusal(f"{path}: const mismatch")
        if "enum" in schema:
            enum = schema["enum"]
            if not isinstance(enum, list) or not any(_same(instance, item) for item in enum):
                raise Refusal(f"{path}: enum mismatch")

        if isinstance(instance, str):
            if "minLength" in schema and len(instance) < schema["minLength"]:
                raise Refusal(f"{path}: minLength")
            if "pattern" in schema:
                try:
                    matched = re.search(schema["pattern"], instance) is not None
                except re.error as exc:
                    raise Refusal(f"{path}: invalid schema pattern") from exc
                if not matched:
                    raise Refusal(f"{path}: pattern")

        if _is_integer(instance) or isinstance(instance, float) and not isinstance(instance, bool):
            if "minimum" in schema and instance < schema["minimum"]:
                raise Refusal(f"{path}: minimum")
            if "maximum" in schema and instance > schema["maximum"]:
                raise Refusal(f"{path}: maximum")

        if isinstance(instance, list):
            if "minItems" in schema and len(instance) < schema["minItems"]:
                raise Refusal(f"{path}: minItems")
            if "maxItems" in schema and len(instance) > schema["maxItems"]:
                raise Refusal(f"{path}: maxItems")
            if schema.get("uniqueItems"):
                serialized = [canonical_bytes(item) for item in instance]
                if len(serialized) != len(set(serialized)):
                    raise Refusal(f"{path}: uniqueItems")
            prefix = schema.get("prefixItems", [])
            if prefix:
                for index, subschema in enumerate(prefix[: len(instance)]):
                    self._validate(instance[index], subschema, f"{path}[{index}]")
            if "items" in schema:
                start = len(prefix)
                items_schema = schema["items"]
                for index in range(start, len(instance)):
                    self._validate(instance[index], items_schema, f"{path}[{index}]")

        if isinstance(instance, dict):
            if "minProperties" in schema and len(instance) < schema["minProperties"]:
                raise Refusal(f"{path}: minProperties")
            required = schema.get("required", [])
            if not isinstance(required, list) or not all(isinstance(item, str) for item in required):
                raise Refusal(f"{path}: malformed required")
            missing = [item for item in required if item not in instance]
            if missing:
                raise Refusal(f"{path}: missing required {missing}")
            properties = schema.get("properties", {})
            if not isinstance(properties, dict):
                raise Refusal(f"{path}: malformed properties")
            for key, subschema in properties.items():
                if key in instance:
                    self._validate(instance[key], subschema, f"{path}.{key}")
            extras = [key for key in instance if key not in properties]
            additional = schema.get("additionalProperties", True)
            if additional is False and extras:
                raise Refusal(f"{path}: additional properties {extras}")
            if isinstance(additional, dict):
                for key in extras:
                    self._validate(instance[key], additional, f"{path}.{key}")

        for index, subschema in enumerate(schema.get("allOf", [])):
            self._validate(instance, subschema, f"{path}.allOf[{index}]")
        if "oneOf" in schema:
            matches = sum(self.is_valid(instance, subschema) for subschema in schema["oneOf"])
            if matches != 1:
                raise Refusal(f"{path}: oneOf matched {matches} branches")
        if "if" in schema:
            branch = "then" if self.is_valid(instance, schema["if"]) else "else"
            if branch in schema:
                self._validate(instance, schema[branch], f"{path}.{branch}")


def collect_local_refs(schema: Any) -> list[str]:
    refs: list[str] = []

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "$ref":
                    if not isinstance(item, str):
                        raise Refusal("non-string local reference")
                    refs.append(item)
                else:
                    visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    visit(schema)
    return refs


def verify_local_refs(schema: dict[str, Any]) -> tuple[int, int]:
    refs = collect_local_refs(schema)
    for reference in refs:
        _resolve_pointer(schema, reference)
    return len(refs), len(set(refs))


def apply_json_patch(instance: Any, operations: list[dict[str, Any]]) -> Any:
    """Apply the replace-only frozen mutation format used by accepted fixtures."""

    value = deepcopy(instance)
    for operation in operations:
        if operation.get("op") != "replace" or not isinstance(operation.get("path"), str):
            raise Refusal("unsupported schema fixture patch")
        tokens = [token.replace("~1", "/").replace("~0", "~") for token in operation["path"].lstrip("/").split("/") if token != ""]
        target = value
        for token in tokens[:-1]:
            target = target[int(token)] if isinstance(target, list) else target[token]
        last = tokens[-1]
        if isinstance(target, list):
            target[int(last)] = deepcopy(operation["value"])
        else:
            target[last] = deepcopy(operation["value"])
    return value
