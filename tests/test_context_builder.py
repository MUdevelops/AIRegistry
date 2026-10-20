import os
import shutil
import sys
import tempfile
import unittest

from _helpers import load_component, release_dir

cb = load_component("context-builder", "context_builder")
kr = load_component("keyword-rag", "keyword_rag")


class TestFormat(unittest.TestCase):
    def test_numbered_block_with_ids(self):
        out = cb.format_context([{"id": "d1", "text": "alpha"}, {"text": "beta"}, "gamma"])
        self.assertEqual(out, "<context>\n[1] (d1) alpha\n[2] (2) beta\n[3] gamma\n</context>")

    def test_whitespace_collapsed_and_header(self):
        out = cb.format_context(["a \n  b\t c"], header="Sources")
        self.assertEqual(out, "<sources>\n[1] a b c\n</sources>")

    def test_budget_is_exact_for_the_lines(self):
        passages = ["x" * 20, "y" * 20, "z" * 20]
        body = lambda s: s.split("\n")[1:-1]
        for limit in (10, 23, 24, 30, 47, 48, 60, 200):
            out = cb.format_context(passages, limit)
            self.assertLessEqual(len("\n".join(body(out))) if out else 0, limit, limit)

    def test_truncation_adds_ellipsis_only_when_there_is_room(self):
        out = cb.format_context(["x" * 100], 40)
        self.assertIn("...", out)
        self.assertEqual(cb.format_context(["x" * 100], 20), "")
        self.assertEqual(cb.format_context([], 100), "")

    def test_drops_passages_after_the_first_that_does_not_fit(self):
        out = cb.format_context(["a" * 30, "b" * 200, "c" * 5], 80)
        self.assertIn("[1]", out)
        self.assertIn("...", out)
        self.assertNotIn("[3]", out)

    def test_validation(self):
        with self.assertRaises(ValueError):
            cb.format_context(["a"], 0)
        with self.assertRaises(TypeError):
            cb.format_context(["a"], "5")
        with self.assertRaises(ValueError):
            cb.format_context(["a"], 10, header="bad header")
        with self.assertRaises(ValueError):
            cb.format_context(["a"], 10, header="</x>")
        with self.assertRaises(TypeError):
            cb.format_context("just a string")
        with self.assertRaises(TypeError):
            cb.format_context([5])
        with self.assertRaises(TypeError):
            cb.format_context([{"id": 1}])


class TestBuild(unittest.TestCase):
    docs = ["Cats purr when happy", "Python is a programming language", "Dogs bark"]

    def test_with_custom_retriever(self):
        calls = []

        def retrieve(documents, query, top_k):
            calls.append((list(documents), query, top_k))
            return ["found"]

        self.assertEqual(cb.build_context("q", self.docs, 2, retrieve=retrieve), "<context>\n[1] found\n</context>")
        self.assertEqual(calls, [(self.docs, "q", 2)])

    def test_with_keyword_rag_results(self):
        out = cb.build_context("python language", self.docs, 1, retrieve=kr.retrieve)
        self.assertIn("(1) Python is a programming language", out)

    def test_default_retriever_uses_importable_keyword_rag(self):
        sys.path.insert(0, os.path.join(release_dir("keyword-rag", "1.1.0"), "src"))
        self.addCleanup(sys.path.remove, sys.path[0])
        self.addCleanup(sys.modules.pop, "keyword_rag", None)
        self.assertIn("Python", cb.build_context("python", self.docs, 1))

    def test_default_retriever_finds_sibling_install_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(release_dir("context-builder", "1.1.0"), "src", "context_builder.py")
            kr_src = os.path.join(release_dir("keyword-rag", "1.1.0"), "src", "keyword_rag.py")
            for source, folder, name in ((src, "context-builder", "context_builder.py"), (kr_src, "keyword-rag", "keyword_rag.py")):
                os.makedirs(os.path.join(tmp, folder, "src"))
                shutil.copyfile(source, os.path.join(tmp, folder, "src", name))
            import importlib.util
            spec = importlib.util.spec_from_file_location("cb_installed", os.path.join(tmp, "context-builder", "src", "context_builder.py"))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            sys.modules.pop("keyword_rag", None)
            self.assertIn("Python", mod.build_context("python", self.docs, 1))
            self.assertNotIn(os.path.join(tmp, "keyword-rag", "src"), sys.path)

    def test_missing_retriever_gives_actionable_error(self):
        sys.modules.pop("keyword_rag", None)
        if any("keyword-rag" in p for p in sys.path):
            self.skipTest("keyword-rag is importable here")
        with self.assertRaisesRegex(ImportError, "ai add keyword-rag"):
            cb.build_context("q", self.docs)

    def test_validation(self):
        with self.assertRaises(TypeError):
            cb.build_context(5, self.docs, retrieve=kr.retrieve)
        with self.assertRaises(ValueError):
            cb.build_context("q", self.docs, 0, retrieve=kr.retrieve)


if __name__ == "__main__":
    unittest.main()
