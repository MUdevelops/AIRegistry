"""agent: a small, deterministic tool-calling loop with a pluggable planner.

You supply a *planner* (rules, a state machine or an LLM wrapper) that looks at
the goal and the steps taken so far and returns the next tool call, or ``None``
to stop. The loop executes the call, records the outcome and repeats, bounded by
``max_steps``. Tool failures are recorded, never raised.
Standard library only. Python 3.9+.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple, Union

__all__ = ["Step", "AgentRun", "run_agent", "__version__"]
__version__ = "1.0.0"

Action = Union[Tuple[str, Mapping[str, Any]], Mapping[str, Any]]
Planner = Callable[[str, Sequence["Step"]], Optional[Action]]


@dataclass(frozen=True)
class Step:
    """One executed (or rejected) action."""

    index: int
    tool: str
    arguments: Dict[str, Any]
    ok: bool
    result: Any = None
    error: Optional[str] = None


@dataclass
class AgentRun:
    """The complete record of a run.

    ``stop_reason`` is ``"planner_done"`` (planner returned ``None``), ``"max_steps"``
    (step limit reached) or ``"error"`` (a step failed with ``stop_on_error=True``).
    """

    goal: str
    steps: List[Step] = field(default_factory=list)
    stop_reason: str = "planner_done"

    @property
    def finished(self) -> bool:
        """``True`` when the planner decided it was done."""
        return self.stop_reason == "planner_done"

    @property
    def final(self) -> Any:
        """Result of the most recent successful step, or ``None``."""
        for step in reversed(self.steps):
            if step.ok:
                return step.result
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal": self.goal,
            "stop_reason": self.stop_reason,
            "finished": self.finished,
            "steps": [
                {"index": s.index, "tool": s.tool, "arguments": dict(s.arguments),
                 "ok": s.ok, "result": s.result, "error": s.error}
                for s in self.steps
            ],
        }


def _parse_action(action: Any) -> Tuple[str, Dict[str, Any]]:
    """Return ``(tool, arguments)`` or raise ``ValueError`` describing the problem."""
    if isinstance(action, Mapping):
        name = action.get("tool", action.get("name"))
        arguments = action.get("arguments")
    elif isinstance(action, (tuple, list)) and len(action) in (1, 2):
        name = action[0]
        arguments = action[1] if len(action) == 2 else None
    else:
        raise ValueError("action must be (tool, arguments) or {'tool': ..., 'arguments': ...}")
    if not isinstance(name, str) or not name:
        raise ValueError("action needs a non-empty tool name")
    if arguments is None:
        arguments = {}
    if not isinstance(arguments, Mapping):
        raise ValueError("action arguments must be a mapping")
    return name, dict(arguments)


def _execute(tools: Any, name: str, arguments: Dict[str, Any]) -> Tuple[bool, Any, Optional[str]]:
    """Run one tool against a mapping of callables or a ``tool-router`` style object."""
    route = getattr(tools, "route", None)
    if callable(route):
        outcome = route({"name": name, "arguments": arguments})
        if outcome.get("ok"):
            return True, outcome.get("result"), None
        return False, None, str(outcome.get("error", "tool failed"))
    if not isinstance(tools, Mapping):
        raise TypeError("tools must be a mapping of name -> callable, or an object with route()")
    func = tools.get(name)
    if not callable(func):
        return False, None, f"unknown tool: {name!r}"
    try:
        return True, func(**arguments), None
    except Exception as exc:  # tool failures are data for the planner
        return False, None, f"{type(exc).__name__}: {exc}"


def run_agent(
    goal: str,
    planner: Planner,
    tools: Any,
    *,
    max_steps: int = 8,
    stop_on_error: bool = False,
) -> AgentRun:
    """Run the plan-act loop.

    Args:
        goal: The task description handed to the planner.
        planner: ``planner(goal, steps) -> action | None``. An action is
            ``(tool_name, arguments)`` or ``{"tool": name, "arguments": {...}}``. ``steps`` is the
            history so far, so a planner can react to earlier results and errors.
        tools: A mapping ``name -> callable`` or an object with ``route({"name", "arguments"})``
            such as the ``tool-router`` component's ``ToolRouter``.
        max_steps: Upper bound on executed actions (>= 1).
        stop_on_error: Stop after the first failed step instead of letting the planner recover.

    Returns:
        An :class:`AgentRun`. Malformed actions and tool errors become failed steps; exceptions
        raised by the planner itself propagate.
    """
    if not isinstance(goal, str):
        raise TypeError("goal must be a string")
    if not callable(planner):
        raise TypeError("planner must be callable")
    if not isinstance(max_steps, int) or isinstance(max_steps, bool) or max_steps < 1:
        raise ValueError("max_steps must be a positive integer")

    run = AgentRun(goal=goal)
    for index in range(max_steps):
        action = planner(goal, tuple(run.steps))
        if action is None:
            run.stop_reason = "planner_done"
            return run
        try:
            name, arguments = _parse_action(action)
        except ValueError as exc:
            run.steps.append(Step(index, "", {}, False, error=f"invalid action: {exc}"))
        else:
            ok, result, error = _execute(tools, name, arguments)
            run.steps.append(Step(index, name, arguments, ok, result, error))
        if stop_on_error and not run.steps[-1].ok:
            run.stop_reason = "error"
            return run
    run.stop_reason = "max_steps"
    return run
