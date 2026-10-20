# tool-router

**Version 1.1.0** · Python 3.9+ · standard library only · MIT

Register plain Python functions as named tools and execute tool calls safely. Errors are returned as data, so a failing tool never crashes your agent loop.

## Install

```bash
ai add tool-router@1.1.0
```

## Quick start

```python
from tool_router import ToolRouter

router = ToolRouter()

@router.tool("add", "Add two numbers",
             parameters={"type": "object", "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
                         "required": ["a", "b"]})
def add(a, b):
    return a + b

router.call("add", a=2, b=3)                    # {'ok': True, 'result': 5}
router.call("add", a=2)                         # {'ok': False, 'error': "TypeError: ...", 'error_type': 'TypeError'}
router.call("nope")                             # {'ok': False, 'error': "unknown tool: 'nope'", 'error_type': 'UnknownTool'}
router.route({"name": "add", "arguments": {"a": 1, "b": 1}})   # a parsed model tool call
router.list_tools()                             # specs you can send to a model
```

## API

| Method | Description |
|---|---|
| `register(name, func, description="", parameters=None)` | Add a tool. Duplicate names raise `ValueError`. |
| `@tool(name=None, description="", parameters=None)` | Decorator form; the function name is the default tool name. |
| `unregister(name)` | Remove a tool; `KeyError` if missing. |
| `call(name, **arguments)` | Run a tool with keyword arguments. |
| `route({"name", "arguments"})` | Run a request mapping; also safe for an argument called `name`. |
| `list_tools()` | `[{"name", "description", "parameters"}]` sorted by name. |
| `has_tool(name)`, `name in router`, `len(router)` | Introspection. |

## Result shape

- Success: `{"ok": True, "result": <value>}`
- Failure: `{"ok": False, "error": "<Type>: <message>", "error_type": "<Type>"}`. `error_type` is `UnknownTool` or `InvalidRequest` for routing problems, otherwise the exception class name.

## Behavior

- Tool names are 1-64 characters (letters, digits, `_`, `-`, `.`), starting with a letter or `_`.
- Tools are called with keyword arguments only.
- Registration mistakes (bad name, non-callable, duplicate) raise immediately; **calls** never raise.
- The router does not sandbox tools. Only register functions you are willing to let a model invoke.

## Changes in 1.1.0

Adds `parameters` specs, `unregister`, `has_tool`/`in`/`len`, `error_type` on failures, name validation, and a safe `route()` for arguments named `name`. Existing `ok`/`result`/`error` fields are unchanged.
