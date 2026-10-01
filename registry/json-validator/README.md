# json-validator

Validate JSON text and return error position, type, keys and optional schema errors.

## Install

```bash
ai add json-validator
```

Python standard library only.

## API

`validate_json(text, schema=None)` returns `{valid, error, line, column, type, keys, schema_errors}`. The optional schema supports `type`, `required`, `properties` and `items`.

## Example

```python
from json_validator import validate_json

print(validate_json('{"a": 1}', {"type": "object", "required": ["a", "b"]}))
print(validate_json('{bad'))
```
