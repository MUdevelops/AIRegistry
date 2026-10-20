# json-validator

**Version 1.1.0** · Python 3.9+ · standard library only · MIT

Validate JSON text and get actionable diagnostics: error line and column, top-level type, object keys, and readable schema violations. Useful for checking structured output from an LLM before using it.

## Install

```bash
ai add json-validator@1.1.0
```

## Quick start

```python
from json_validator import validate_json

validate_json('{"name": "Ada", "age": 36}')["valid"]          # True
validate_json('{"name": }')                                    # valid False, error/line/column set

schema = {
    "type": "object",
    "required": ["name", "age"],
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "age": {"type": "integer", "minimum": 0},
    },
    "additionalProperties": False,
}
result = validate_json('{"name": "", "age": -1, "x": 1}', schema)
result["schema_errors"]
# ["$.name: expected at least 1 characters",
#  "$.age: -1 is below the minimum 0",
#  "$: unexpected key 'x'"]
```

## API

`validate_json(text, schema=None)` returns:

| Key | Meaning |
|---|---|
| `valid` | `True` when the text parses and satisfies the schema. |
| `error` | Parse error message, or `None`. |
| `line`, `column` | 1-based error position, or `None`. |
| `type` | `object`, `array`, `string`, `number`, `boolean` or `null`. |
| `keys` | Sorted keys of a top-level object, otherwise `None`. |
| `schema_errors` | List of violations such as `$.user.age: expected integer, got string`. |

`text` may be `str`, `bytes` or `bytearray`.

## Supported schema keywords

`type` (a name or a list of names: `object`, `array`, `string`, `number`, `integer`, `boolean`, `null`), `enum`, `required`, `properties`, `additionalProperties` (boolean), `items`, `minItems`, `maxItems`, `minLength`, `maxLength`, `minimum`, `maximum`. The list is available as `SUPPORTED_KEYWORDS`. Other keywords are ignored.

## Behavior

- Bad JSON never raises; it is reported in the result.
- `NaN`, `Infinity` and `-Infinity` are rejected because they are not valid JSON.
- A malformed **schema** (for example an unknown type name) raises `ValueError`, so authoring mistakes are not mistaken for data errors.
- Booleans are not numbers; `1.0` counts as an `integer`.

## Changes in 1.1.0

Adds `enum`, `additionalProperties`, `minItems`/`maxItems`, `minLength`/`maxLength`, `minimum`/`maximum` and type lists; rejects `NaN`/`Infinity`; validates the schema up front; handles bytes input and excessive nesting. Validity results for 1.0.0 inputs are unchanged; error messages now name JSON types (`string`) instead of Python types (`str`).
