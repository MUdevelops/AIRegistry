import unittest

from _helpers import load_component

pb = load_component("prompt-builder", "prompt_builder")
old = load_component("prompt-builder", "prompt_builder", "1.0.0")


class TestPromptBuilder(unittest.TestCase):
    def test_sections_render_in_fixed_order_and_skip_empty(self):
        p = pb.PromptBuilder(input="in", system="sys", context="", instruction="do")
        self.assertEqual(p.build(), "## System\nsys\n\n## Instruction\ndo\n\n## Input\nin")

    def test_labels_off_and_custom_separator(self):
        p = pb.PromptBuilder(system="a", input="b", separator=" | ")
        self.assertEqual(p.build(labels=False), "a | b")

    def test_placeholders_are_single_pass(self):
        self.assertEqual(pb.build_prompt(input="{a} {b}", a="{b}", b="x"), "## Input\n{b} x")

    def test_unknown_placeholders_kept_unless_strict(self):
        p = pb.PromptBuilder(input="hello {name}")
        self.assertIn("{name}", p.build())
        with self.assertRaisesRegex(ValueError, "name"):
            p.build(strict=True)

    def test_json_braces_are_left_alone(self):
        self.assertIn('{"a": 1}', pb.build_prompt(input='{"a": 1} {x}', x="y"))

    def test_render_accepts_mapping_for_reserved_names(self):
        p = pb.PromptBuilder(input="{labels}")
        self.assertEqual(p.render({"labels": "L"}, labels=False), "L")

    def test_set_chains_validates_and_accepts_none(self):
        p = pb.PromptBuilder().set("input", "x").set("context", None)
        self.assertEqual(p.sections["input"], "x")
        with self.assertRaises(ValueError):
            p.set("bogus", "x")
        with self.assertRaises(TypeError):
            p.set("input", 5)
        with self.assertRaises(TypeError):
            pb.PromptBuilder(system=5)

    def test_sections_property_is_a_copy(self):
        p = pb.PromptBuilder(input="x")
        p.sections["input"] = "changed"
        self.assertEqual(p.sections["input"], "x")

    def test_to_messages(self):
        msgs = pb.PromptBuilder(system="You are {role}.", instruction="Go", input="hi").to_messages({"role": "kind"})
        self.assertEqual(msgs[0], {"role": "system", "content": "You are kind."})
        self.assertEqual(msgs[1]["role"], "user")
        self.assertIn("## Input\nhi", msgs[1]["content"])
        self.assertNotIn("System", msgs[1]["content"])
        self.assertEqual(pb.PromptBuilder().to_messages(), [])

    def test_matches_1_0_0_for_simple_prompts(self):
        kw = dict(system="s", instruction="Say {x}", context="c", input="i")
        self.assertEqual(pb.build_prompt(x="ok", **kw), old.build_prompt(x="ok", **kw))


if __name__ == "__main__":
    unittest.main()
