"""json-validator: validate JSON text and return precise diagnostics.

``validate_json`` never raises for bad JSON. It returns a result dict with the
error position, the top-level type, the object keys and, when a schema is given,
a list of schema violations. The schema language is a small, documented subset
of JSON Schema. Standard library only. Python 3.9+.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

__all__ = ["validate_json", "SUPPORTED_KEYWORDS", "__version__"]
__version__ = "1.1.0"

import json

SUPPORTED_KEYWORDS = (
    "type", "enum", "required", "properties", "additionalProperties", "items",
    "minItems", "maxItems", "minLength", "maxLength", "minimum", "maximum",
)

_TYPE_NAMES = ("object", "array", "string", "number", "integer", "boolean", "null")


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _type_ok(value: Any, name: str) -> bool:
    if name == "object":
        return isinstance(value, dict)
    if name == "array":
        return isinstance(value, list)
    if name == "string":
        return isinstance(value, str)
    if name == "boolean":
        return isinstance(value, bool)
    if name == "null":
        return value is None
    if name == "number":
        return _is_number(value)
    if name == "integer":
        return isinstance(value, int) and not isinstance(value, bool) or (
            isinstance(value, float) and value.is_integer()
        )
    raise ValueError(f"invalid schema: unknown type {name!r}")


def _type_name(value: Any) -> str:
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    if isinstance(value, str):
        return "string"
    if isinstance(value, bool):
        return "boolean"
    if value is None:
        return "null"
    return "number"


def _check_schema(schema: Any, path: str = "schema") -> None:
    """Reject malformed schemas early so authoring mistakes are not reported as data errors."""
    if not isinstance(schema, dict):
        raise ValueError(f"invalid schema: {path} must be an object")
    kind = schema.get("type")
    if kind is not None:
        names = kind if isinstance(kind, list) else [kind]
        if not names or any(n not in _TYPE_NAMES for n in names):
            raise ValueError(f"invalid schema: {path}.type must be one of {_TYPE_NAMES}")
    required = schema.get("required", [])
    if not isinstance(required, list) or not all(isinstance(k, str) for k in required):
        raise ValueError(f"invalid schema: {path}.required must be a list of strings")
    for key, sub in (schema.get("properties") or {}).items():
        _check_schema(sub, f"{path}.properties.{key}")
    if "items" in schema:
        _check_schema(schema["items"], f"{path}.items")
    extra = schema.get("additionalProperties", True)
    if not isinstance(extra, bool):
        raise ValueError(f"invalid schema: {path}.additionalProperties must be a boolean")
    if "enum" in schema and not isinstance(schema["enum"], list):
        raise ValueError(f"invalid schema: {path}.enum must be a list")
    for key in ("minItems", "maxItems", "minLength", "maxLength"):
        if key in schema and (not isinstance(schema[key], int) or isinstance(schema[key], bool)):
            raise ValueError(f"invalid schema: {path}.{key} must be an integer")
    for key in ("minimum", "maximum"):
        if key in schema and not _is_number(schema[key]):
            raise ValueError(f"invalid schema: {path}.{key} must be a number")


def _check(value: Any, schema: Dict[str, Any], path: str, errors: List[str]) -> None:
    kind = schema.get("type")
    if kind is not None:
        names = kind if isinstance(kind, list) else [kind]
        if not any(_type_ok(value, n) for n in names):
            errors.append(f"{path}: expected {' or '.join(names)}, got {_type_name(value)}")
            return
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: value is not one of the allowed values")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: missing required key '{key}'")
        props = schema.get("properties") or {}
        for key, sub in props.items():
            if key in value:
                _check(value[key], sub, f"{path}.{key}", errors)
        if schema.get("additionalProperties") is False:
            for key in sorted(set(value) - set(props)):
                errors.append(f"{path}: unexpected key '{key}'")
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{path}: expected at least {schema['minItems']} items, got {len(value)}")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(f"{path}: expected at most {schema['maxItems']} items, got {len(value)}")
        if "items" in schema:
            for i, item in enumerate(value):
                _check(item, schema["items"], f"{path}[{i}]", errors)
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"{path}: expected at least {schema['minLength']} characters")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append(f"{path}: expected at most {schema['maxLength']} characters")
    if _is_number(value):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: {value} is below the minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: {value} is above the maximum {schema['maximum']}")


class _NonFinite(ValueError):
    pass


def _reject_constant(name: str) -> Any:
    raise _NonFinite(f"{name} is not valid JSON")


def validate_json(
    text: Union[str, bytes, bytearray],
    schema: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Validate JSON ``text`` and optionally check it against ``schema``.

    Returns a dict with these keys:

    - ``valid``: ``True`` if the text parses and satisfies the schema.
    - ``error``: parse error message, or ``None``.
    - ``line`` / ``column``: 1-based position of a parse error, or ``None``.
    - ``type``: ``object``, ``array``, ``string``, ``number``, ``boolean`` or ``null``.
    - ``keys``: sorted keys of a top-level object, otherwise ``None``.
    - ``schema_errors``: list of readable violations, each prefixed with a path such as ``$.user.age``.

    ``NaN`` and ``Infinity`` are rejected because they are not valid JSON.

    Raises:
        ValueError: ``schema`` itself is malformed (unknown type name, wrong keyword value types).
    """
    if schema is not None:
        _check_schema(schema)
    result: Dict[str, Any] = {
        "valid": False, "error": None, "line": None, "column": None,
        "type": None, "keys": None, "schema_errors": [],
    }
    if not isinstance(text, (str, bytes, bytearray)):
        result["error"] = f"text must be str or bytes, got {type(text).__name__}"
        return result
    try:
        data = json.loads(text, parse_constant=_reject_constant)
    except json.JSONDecodeError as exc:
        result.update(error=exc.msg, line=exc.lineno, column=exc.colno)
        return result
    except _NonFinite as exc:
        result["error"] = str(exc)
        return result
    except RecursionError:
        result["error"] = "JSON is nested too deeply"
        return result
    except UnicodeDecodeError as exc:
        result["error"] = f"invalid encoding: {exc.reason}"
        return result
    result["type"] = _type_name(data)
    if isinstance(data, dict):
        result["keys"] = sorted(data)
    if schema:
        _check(data, schema, "$", result["schema_errors"])
    result["valid"] = not result["schema_errors"]
    return result
