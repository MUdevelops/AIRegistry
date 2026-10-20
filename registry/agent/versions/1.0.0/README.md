# agent

**Version 1.0.0** · Python 3.9+ · standard library only · MIT

A small, deterministic tool-calling loop with a pluggable planner. Bring your own decision logic (rules, a state machine or an LLM wrapper); the loop executes tool calls, records every outcome and stops safely.

```text
planner(goal, steps) -> action | None  ->  execute tool  ->  record Step  ->  repeat (<= max_steps)
```

## Install

```bash
ai add agent@1.0.0
```

Optional: `ai add tool-router@1.1.0` for a router with parameter specs. Any object with `route({"name", "arguments"})` works.

## Quick start

```python
from agent import run_agent

tools = {
    "search": lambda query: ["AIRegistry installs reusable AI components."],
    "shout": lambda text: text.upper(),
}

def planner(goal, steps):
    if not steps:
        return ("search", {"query": goal})
    if len(steps) == 1 and steps[0].ok:
        return ("shout", {"text": steps[0].result[0]})
    return None                                  # done

run = run_agent("what is AIRegistry", planner, tools, max_steps=5)
run.final          # 'AIREGISTRY INSTALLS REUSABLE AI COMPONENTS.'
run.stop_reason    # 'planner_done'
run.finished       # True
```

With `tool-router`:

```python
from tool_router import ToolRouter
router = ToolRouter()
router.register("shout", lambda text: text.upper())
run = run_agent("hi", lambda goal, steps: None if steps else ("shout", {"text": goal}), router)
run.final          # 'HI'
```

## API

`run_agent(goal, planner, tools, *, max_steps=8, stop_on_error=False) -> AgentRun`

| Name | Description |
|---|---|
| `planner(goal, steps)` | Returns `(tool, arguments)`, `{"tool": ..., "arguments": {...}}`, or `None` to stop. `steps` is a tuple of `Step`. |
| `tools` | Mapping `name -> callable`, or an object with `route(request)` (such as `ToolRouter`). |
| `Step` | `index`, `tool`, `arguments`, `ok`, `result`, `error`. |
| `AgentRun` | `goal`, `steps`, `stop_reason`, `.finished`, `.final`, `.to_dict()`. |

`stop_reason` is `"planner_done"`, `"max_steps"` or `"error"` (only with `stop_on_error=True`).

## Behavior

- Tools are called with keyword arguments. A failing tool becomes a `Step` with `ok=False` and an `error` string; the planner sees it and can retry or choose another tool.
- A malformed action (wrong shape, empty tool name, non-mapping arguments) is recorded as a failed step with tool `""` instead of crashing the loop.
- The loop never runs more than `max_steps` actions.
- Exceptions raised by the **planner** propagate, since they indicate a bug in your planner.
- The loop does not sandbox tools. Only expose tools you trust the planner to call.

## Changes in 1.0.0

Replaces the 0.1.0 prototype with a documented, typed loop: structured `Step`/`AgentRun` records, error capture, `stop_on_error`, and `ToolRouter` support. The prototype's `run(goal, tools, plan, max_steps)` function is removed.
