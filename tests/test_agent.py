import unittest

from _helpers import load_component

ag = load_component("agent", "agent")
tr = load_component("tool-router", "tool_router")

TOOLS = {"double": lambda x: x * 2, "fail": lambda: 1 / 0}


def script(*actions):
    """A planner that replays ``actions`` and then stops."""
    def planner(goal, steps):
        return actions[len(steps)] if len(steps) < len(actions) else None
    return planner


class TestAgent(unittest.TestCase):
    def test_runs_until_planner_stops(self):
        run = ag.run_agent("g", script(("double", {"x": 2}), {"tool": "double", "arguments": {"x": 5}}), TOOLS)
        self.assertEqual([s.result for s in run.steps], [4, 10])
        self.assertEqual((run.final, run.stop_reason, run.finished), (10, "planner_done", True))
        self.assertEqual(run.steps[0].index, 0)

    def test_planner_sees_goal_and_history(self):
        seen = []

        def planner(goal, steps):
            seen.append((goal, len(steps), isinstance(steps, tuple)))
            return ("double", {"x": 1}) if not steps else None

        ag.run_agent("my goal", planner, TOOLS)
        self.assertEqual(seen, [("my goal", 0, True), ("my goal", 1, True)])

    def test_tool_errors_are_recorded_and_planner_can_recover(self):
        def planner(goal, steps):
            if not steps:
                return ("fail", {})
            if not steps[-1].ok:
                return ("double", {"x": 3})
            return None

        run = ag.run_agent("g", planner, TOOLS)
        self.assertFalse(run.steps[0].ok)
        self.assertIn("ZeroDivisionError", run.steps[0].error)
        self.assertEqual((run.final, run.finished), (6, True))

    def test_stop_on_error(self):
        run = ag.run_agent("g", script(("fail", {}), ("double", {"x": 1})), TOOLS, stop_on_error=True)
        self.assertEqual((len(run.steps), run.stop_reason, run.finished, run.final), (1, "error", False, None))

    def test_max_steps_bounds_the_loop(self):
        run = ag.run_agent("g", lambda g, s: ("double", {"x": 1}), TOOLS, max_steps=3)
        self.assertEqual((len(run.steps), run.stop_reason, run.finished), (3, "max_steps", False))

    def test_unknown_tool_and_bad_arguments(self):
        run = ag.run_agent("g", script(("nope", {}), ("double", {"y": 1})), TOOLS)
        self.assertIn("unknown tool", run.steps[0].error)
        self.assertIn("TypeError", run.steps[1].error)

    def test_malformed_actions_become_failed_steps(self):
        for action in (5, "double", (), ("double", 5, 6), {"arguments": {}}, {"tool": ""}, ("double", [1]), (3, {})):
            run = ag.run_agent("g", script(action), TOOLS)
            self.assertFalse(run.steps[0].ok, action)
            self.assertTrue(run.steps[0].error.startswith("invalid action"), action)
            self.assertEqual(run.steps[0].tool, "")

    def test_one_tuple_and_name_key(self):
        tools = {"ping": lambda: "pong"}
        self.assertEqual(ag.run_agent("g", script(("ping",)), tools).final, "pong")
        self.assertEqual(ag.run_agent("g", script({"name": "ping"}), tools).final, "pong")

    def test_works_with_tool_router(self):
        router = tr.ToolRouter()
        router.register("double", lambda x: x * 2)
        run = ag.run_agent("g", script(("double", {"x": 4}), ("missing", {})), router)
        self.assertEqual(run.steps[0].result, 8)
        self.assertIn("unknown tool", run.steps[1].error)
        self.assertEqual(run.final, 8)

    def test_arguments_are_copied(self):
        args = {"x": 1}
        run = ag.run_agent("g", script(("double", args)), TOOLS)
        args["x"] = 99
        self.assertEqual(run.steps[0].arguments, {"x": 1})

    def test_planner_exceptions_propagate(self):
        def planner(goal, steps):
            raise RuntimeError("planner bug")

        with self.assertRaisesRegex(RuntimeError, "planner bug"):
            ag.run_agent("g", planner, TOOLS)

    def test_to_dict_is_json_friendly(self):
        import json
        data = ag.run_agent("g", script(("double", {"x": 2})), TOOLS).to_dict()
        self.assertEqual(json.loads(json.dumps(data))["steps"][0]["result"], 4)
        self.assertEqual(data["stop_reason"], "planner_done")

    def test_argument_validation(self):
        with self.assertRaises(TypeError):
            ag.run_agent(5, script(), TOOLS)
        with self.assertRaises(TypeError):
            ag.run_agent("g", None, TOOLS)
        for bad in (0, -1, True, "3"):
            with self.assertRaises(ValueError):
                ag.run_agent("g", script(), TOOLS, max_steps=bad)
        with self.assertRaises(TypeError):
            ag.run_agent("g", script(("double", {})), ["not", "tools"])

    def test_empty_run(self):
        run = ag.run_agent("g", script(), TOOLS)
        self.assertEqual((run.steps, run.final, run.finished), ([], None, True))


if __name__ == "__main__":
    unittest.main()
