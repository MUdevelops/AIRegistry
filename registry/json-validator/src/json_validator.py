"""json-validator: validate JSON text and return useful diagnostics."""
import json

TYPES = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None)}


def _type_ok(value, name):
    if name == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if name == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    return isinstance(value, TYPES[name]) if name in TYPES else False


def _check(value, schema, path, errors):
    t = schema.get("type")
    if t and not _type_ok(value, t):
        errors.append(f"{path}: expected {t}, got {type(value).__name__}")
        return
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: missing required key '{key}'")
        for key, sub in schema.get("properties", {}).items():
            if key in value:
                _check(value[key], sub, f"{path}.{key}", errors)
    if isinstance(value, list) and "items" in schema:
        for i, item in enumerate(value):
            _check(item, schema["items"], f"{path}[{i}]", errors)


def validate_json(text, schema=None):
    """Return {valid, error, line, column, type, keys, schema_errors}.

    schema is an optional small subset of JSON Schema: type, required, properties, items.
    """
    result = {"valid": False, "error": None, "line": None, "column": None,
              "type": None, "keys": None, "schema_errors": []}
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        result.update(error=e.msg, line=e.lineno, column=e.colno)
        return result
    except TypeError as e:
        result["error"] = str(e)
        return result
    result["type"] = {dict: "object", list: "array", str: "string", bool: "boolean",
                      type(None): "null"}.get(type(data), "number")
    if isinstance(data, dict):
        result["keys"] = sorted(data)
    if schema:
        _check(data, schema, "$", result["schema_errors"])
    result["valid"] = not result["schema_errors"]
    return result
