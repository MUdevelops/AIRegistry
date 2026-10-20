import unittest

from _helpers import load_component

tr = load_component("tool-router", "tool_router")


def make():
    router = tr.ToolRouter()
    router.register("add", lambda a, b: a + b, "Add numbers")
    return router


class TestRouter(unittest.TestCase):
    def test_call_success_and_errors(self):
        r = make()
        self.assertEqual(r.call("add", a=1, b=2), {"ok": True, "result": 3})
        bad = r.call("add", a=1)
        self.assertFalse(bad["ok"])
        self.assertEqual(bad["error_type"], "TypeError")
        self.assertTrue(bad["error"].startswith("TypeError:"))
        unknown = r.call("nope")
        self.assertEqual((unknown["ok"], unknown["error_type"]), (False, "UnknownTool"))
        self.assertIn("'nope'", unknown["error"])

    def test_tool_exceptions_are_contained(self):
        r = tr.ToolRouter()
        r.register("boom", lambda: 1 / 0)
        out = r.call("boom")
        self.assertEqual((out["ok"], out["error_type"]), (False, "ZeroDivisionError"))

    def test_route_validates_requests(self):
        r = make()
        self.assertEqual(r.route({"name": "add", "arguments": {"a": 1, "b": 1}})["result"], 2)
        self.assertEqual(r.route({"name": "add", "arguments": None})["error_type"], "TypeError")
        for bad in (None, [], {"arguments": {}}, {"name": 5}):
            self.assertEqual(r.route(bad)["error_type"], "InvalidRequest")
        self.assertEqual(r.route({"name": "add", "arguments": [1]})["error_type"], "InvalidRequest")

    def test_argument_named_name_works_through_route(self):
        r = tr.ToolRouter()
        r.register("greet", lambda name: f"hi {name}")
        self.assertEqual(r.route({"name": "greet", "arguments": {"name": "Ada"}})["result"], "hi Ada")

    def test_decorator(self):
        r = tr.ToolRouter()

        @r.tool(description="Double", parameters={"type": "object", "properties": {"x": {"type": "number"}}})
        def double(x):
            return x * 2

        self.assertEqual(double(2), 4)
        self.assertEqual(r.call("double", x=4)["result"], 8)
        self.assertEqual(r.list_tools()[0]["parameters"]["properties"]["x"]["type"], "number")

    def test_registration_rules(self):
        r = make()
        with self.assertRaises(ValueError):
            r.register("add", len)
        for bad in ("", " x", "1abc", "a b", "x" * 65, None, 5):
            with self.assertRaises(ValueError, msg=repr(bad)):
                r.register(bad, len)
        with self.assertRaises(TypeError):
            r.register("ok", "not callable")
        with self.assertRaises(TypeError):
            r.register("ok", len, parameters=[])
        r.register("dotted.name-1", len)

    def test_introspection_and_unregister(self):
        r = make()
        r.register("alpha", len)
        self.assertEqual([t["name"] for t in r.list_tools()], ["add", "alpha"])
        self.assertEqual(r.list_tools()[0]["parameters"], {"type": "object", "properties": {}})
        self.assertTrue("add" in r and r.has_tool("alpha") and len(r) == 2)
        r.unregister("alpha")
        self.assertNotIn("alpha", r)
        with self.assertRaises(KeyError):
            r.unregister("alpha")

    def test_list_tools_returns_copies(self):
        r = make()
        r.list_tools()[0]["parameters"]["x"] = 1
        self.assertNotIn("x", r.list_tools()[0]["parameters"])


if __name__ == "__main__":
    unittest.main()
