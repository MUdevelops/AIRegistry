import os, sys, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for c in ("prompt-builder", "text-chunker", "json-validator", "citation-builder",
          "conversation-memory", "keyword-rag", "context-builder", "tool-router"):
    sys.path.insert(0, os.path.join(ROOT, "registry", c, "src"))

from prompt_builder import PromptBuilder, build_prompt  # noqa: E402
from text_chunker import chunk_text, chunk_with_offsets  # noqa: E402
from json_validator import validate_json  # noqa: E402
from citation_builder import build_citations, markers  # noqa: E402
from conversation_memory import ConversationMemory  # noqa: E402
from keyword_rag import retrieve  # noqa: E402
from context_builder import build_context, format_context  # noqa: E402
from tool_router import ToolRouter  # noqa: E402


class TestComponents(unittest.TestCase):
    def test_prompt_builder(self):
        p = build_prompt(instruction="Say {x}", input="hi", x="ok")
        self.assertIn("Say ok", p)
        self.assertEqual(PromptBuilder(system="s", input="i").to_messages()[0]["role"], "system")
        with self.assertRaises(ValueError):
            PromptBuilder().set("bogus", "x")

    def test_chunker(self):
        self.assertEqual(chunk_text("abcdefghij", 4, 1), ["abcd", "defg", "ghij"])
        self.assertEqual(chunk_text("a b c d e", 3, 1, "words"), ["a b c", "c d e"])
        self.assertEqual(chunk_text("", 3, 1), [])
        self.assertEqual(chunk_with_offsets("abcdef", 4, 2)[1]["start"], 2)
        with self.assertRaises(ValueError):
            chunk_text("abc", 2, 2)

    def test_json_validator(self):
        bad = validate_json("{bad")
        self.assertFalse(bad["valid"])
        self.assertEqual(bad["line"], 1)
        ok = validate_json('{"a": 1}', {"type": "object", "required": ["a"], "properties": {"a": {"type": "integer"}}})
        self.assertTrue(ok["valid"])
        self.assertEqual(ok["keys"], ["a"])
        r = validate_json('{"a": "x"}', {"required": ["b"], "properties": {"a": {"type": "integer"}}})
        self.assertEqual(len(r["schema_errors"]), 2)

    def test_citations(self):
        c = build_citations([{"title": "A", "url": "u"}, {"title": "A", "url": "u"}, {"title": "B", "author": "Z"}])
        self.assertEqual(c, ["[1] A. u", "[2] Z. B."])
        self.assertEqual(markers([3, 1, 1]), "[1][3]")

    def test_memory(self):
        m = ConversationMemory(max_messages=2)
        m.add("user", "green apples")
        m.add("assistant", "blue sky")
        m.add("user", "green tea")
        self.assertEqual(len(m), 2)
        self.assertEqual(m.search("green")[0]["content"], "green tea")
        m.clear()
        self.assertEqual(m.to_list(), [])

    def test_rag_and_context(self):
        docs = ["Cats purr when happy", "Python is a programming language", "Dogs bark"]
        r = retrieve(docs, "python language", 2)
        self.assertEqual(r[0]["id"], 1)
        self.assertEqual(retrieve(docs, "zzz"), [])
        ctx = build_context("python", docs, top_k=1)
        self.assertIn("Python is a programming language", ctx)
        self.assertEqual(format_context([]), "")
        self.assertLessEqual(len(format_context([{"id": 1, "text": "x" * 500}], max_chars=100)), 140)

    def test_router(self):
        r = ToolRouter()
        r.register("add", lambda a, b: a + b)
        self.assertEqual(r.route({"name": "add", "arguments": {"a": 1, "b": 2}}), {"ok": True, "result": 3})
        self.assertFalse(r.call("nope")["ok"])
        self.assertFalse(r.call("add", a=1)["ok"])
        self.assertFalse(r.route("bad")["ok"])
        with self.assertRaises(ValueError):
            r.register("add", len)


if __name__ == "__main__":
    unittest.main()
