# tool-router

Register simple tools and route calls by name, safely rejecting unknown tools.

## Install

```bash
ai add tool-router
```

Python standard library only.

## API

`ToolRouter()` with `.register(name, func, description)`, the `@router.tool()` decorator, `.list_tools()`, `.call(name, **args)` and `.route({"name", "arguments"})`. Calls return `{ok, result}` or `{ok: False, error}` and never raise for unknown tools.

## Example

```python
from tool_router import ToolRouter

r = ToolRouter()
r.register("add", lambda a, b: a + b, "Add numbers")
print(r.route({"name": "add", "arguments": {"a": 1, "b": 2}}))
print(r.call("rm"))
```
