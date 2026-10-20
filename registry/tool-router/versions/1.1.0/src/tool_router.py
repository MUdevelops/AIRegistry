"""tool-router: register Python callables as named tools and call them safely.

Calls never raise: they return ``{"ok": True, "result": ...}`` or
``{"ok": False, "error": ..., "error_type": ...}``, which makes the router a good
execution layer for LLM tool calls. Standard library only. Python 3.9+.
"""
from __future__ import annotations

import re
from typing import Any, Callable, Dict, List, Mapping, Optional

__all__ = ["ToolRouter", "__version__"]
__version__ = "1.1.0"

_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]{0,63}$")
_EMPTY_PARAMETERS: Dict[str, Any] = {"type": "object", "properties": {}}


def _failure(message: str, kind: str) -> Dict[str, Any]:
    return {"ok": False, "error": message, "error_type": kind}


class ToolRouter:
    """A registry of named tools."""

    def __init__(self) -> None:
        self._tools: Dict[str, Dict[str, Any]] = {}

    # -- registration ------------------------------------------------------
    def register(
        self,
        name: str,
        func: Callable[..., Any],
        description: str = "",
        parameters: Optional[Mapping[str, Any]] = None,
    ) -> None:
        """Register ``func`` under ``name``.

        Args:
            name: 1-64 characters: letters, digits, ``_``, ``-`` or ``.``; must start with a letter or ``_``.
            func: The callable. It is invoked with keyword arguments only.
            description: Short text for humans and models.
            parameters: Optional JSON-Schema-style description of the arguments, returned by :meth:`list_tools`.
        """
        if not isinstance(name, str) or not _NAME.match(name):
            raise ValueError(
                "tool name must be 1-64 characters: letters, digits, '_', '-' or '.', starting with a letter or '_'"
            )
        if not callable(func):
            raise TypeError("func must be callable")
        if name in self._tools:
            raise ValueError(f"tool {name!r} already registered")
        if parameters is not None and not isinstance(parameters, Mapping):
            raise TypeError("parameters must be a mapping")
        self._tools[name] = {
            "func": func,
            "description": str(description),
            "parameters": dict(parameters) if parameters is not None else dict(_EMPTY_PARAMETERS),
        }

    def tool(
        self,
        name: Optional[str] = None,
        description: str = "",
        parameters: Optional[Mapping[str, Any]] = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator form: ``@router.tool("add", "Add two numbers")``."""

        def decorate(func: Callable[..., Any]) -> Callable[..., Any]:
            self.register(name or func.__name__, func, description, parameters)
            return func

        return decorate

    def unregister(self, name: str) -> None:
        """Remove a tool. Raises ``KeyError`` if it is not registered."""
        if name not in self._tools:
            raise KeyError(name)
        del self._tools[name]

    # -- inspection --------------------------------------------------------
    def has_tool(self, name: str) -> bool:
        return name in self._tools

    __contains__ = has_tool

    def __len__(self) -> int:
        return len(self._tools)

    def list_tools(self) -> List[Dict[str, Any]]:
        """Tool specs sorted by name: ``{"name", "description", "parameters"}``."""
        return [
            {"name": n, "description": t["description"], "parameters": dict(t["parameters"])}
            for n, t in sorted(self._tools.items())
        ]

    # -- calling -----------------------------------------------------------
    def _invoke(self, name: Any, arguments: Mapping[str, Any]) -> Dict[str, Any]:
        tool = self._tools.get(name) if isinstance(name, str) else None
        if tool is None:
            return _failure(f"unknown tool: {name!r}", "UnknownTool")
        try:
            return {"ok": True, "result": tool["func"](**arguments)}
        except Exception as exc:  # tool failures are reported to the caller, not raised
            return _failure(f"{type(exc).__name__}: {exc}", type(exc).__name__)

    def call(self, name: str, **arguments: Any) -> Dict[str, Any]:
        """Call a tool with keyword arguments.

        An argument that is itself called ``name`` would clash with this method's
        parameter; use :meth:`route` for those.
        """
        return self._invoke(name, arguments)

    def route(self, request: Any) -> Dict[str, Any]:
        """Execute ``{"name": str, "arguments": dict}``, e.g. a parsed model tool call."""
        if not isinstance(request, Mapping) or not isinstance(request.get("name"), str):
            return _failure("request must be {'name': str, 'arguments': dict}", "InvalidRequest")
        arguments = request.get("arguments")
        if arguments is None:
            arguments = {}
        if not isinstance(arguments, Mapping):
            return _failure("arguments must be an object", "InvalidRequest")
        return self._invoke(request["name"], arguments)
