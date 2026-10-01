"""tool-router: register simple tools and route calls by name, rejecting unknown ones."""


class ToolRouter:
    def __init__(self):
        self._tools = {}

    def register(self, name, func, description=""):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("tool name must be a non-empty string")
        if not callable(func):
            raise TypeError("func must be callable")
        if name in self._tools:
            raise ValueError(f"tool {name!r} already registered")
        self._tools[name] = (func, description)

    def tool(self, name=None, description=""):
        """Decorator form: @router.tool('add')"""
        def deco(func):
            self.register(name or func.__name__, func, description)
            return func
        return deco

    def list_tools(self):
        return [{"name": n, "description": d} for n, (_, d) in sorted(self._tools.items())]

    def call(self, name, **arguments):
        """Return {'ok': True, 'result': ...} or {'ok': False, 'error': ...}. Never raises for bad calls."""
        if name not in self._tools:
            return {"ok": False, "error": f"unknown tool: {name!r}"}
        try:
            return {"ok": True, "result": self._tools[name][0](**arguments)}
        except Exception as e:  # tool errors are reported, not propagated
            return {"ok": False, "error": f"{type(e).__name__}: {e}"}

    def route(self, request):
        """request: {'name': str, 'arguments': dict}"""
        if not isinstance(request, dict) or not isinstance(request.get("name"), str):
            return {"ok": False, "error": "request must be {'name': str, 'arguments': dict}"}
        args = request.get("arguments") or {}
        if not isinstance(args, dict):
            return {"ok": False, "error": "arguments must be an object"}
        return self.call(request["name"], **args)
