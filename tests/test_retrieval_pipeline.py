import unittest

from _helpers import load_component

rp = load_component("retrieval-pipeline", "retrieval_pipeline")
kr = load_component("keyword-rag", "keyword_rag")
cb = load_component("context-builder", "context_builder")
qr = load_component("query-rewriter", "query_rewriter")

DOCS = ["Cats purr when happy.", "Python is a programming language.", "AIRegistry installs components."]


def retrieve(query, documents, top_k):
    return [d for d in documents if query.split()[0].lower() in d.lower()][:top_k]


def build(passages, max_chars):
    return "\n".join(f"- {p}" for p in passages)[:max_chars]


class TestPipeline(unittest.TestCase):
    def test_end_to_end_with_real_components(self):
        pipe = rp.RetrievalPipeline(
            lambda q, docs, top_k: kr.retrieve(docs, q, top_k),
            lambda passages, max_chars: cb.format_context(passages, max_chars),
            top_k=2, rewrite_query=lambda q: qr.rewrite_query(q, remove_stopwords=True))
        result = pipe.run("What is the Python language?", DOCS)
        self.assertEqual(result.passages, ("Python is a programming language.",))
        self.assertEqual(result.retrieval_query, "Python language?")
        self.assertEqual(result.context, "<context>\n[1] Python is a programming language.\n</context>")
        self.assertEqual(result.to_dict()["passages"], ["Python is a programming language."])
        self.assertIs(pipe("python", DOCS).__class__, rp.RetrievalResult)

    def test_function_form_returns_context_string(self):
        self.assertEqual(rp.build_retrieval_context("python", DOCS, retrieve=retrieve, build_context=build),
                         "- Python is a programming language.")

    def test_adapters_receive_documented_arguments(self):
        seen = {}

        def r(query, documents, top_k):
            seen["r"] = (query, list(documents), top_k)
            return ["a"]

        def b(passages, max_chars):
            seen["b"] = (passages, max_chars)
            return "ctx"

        rp.RetrievalPipeline(r, b, top_k=7, max_chars=99).run("q", ["d"])
        self.assertEqual(seen, {"r": ("q", ["d"], 7), "b": (["a"], 99)})

    def test_passage_shapes_are_normalized(self):
        pipe = rp.RetrievalPipeline(lambda q, d, top_k: ["  s  ", {"text": "m"}, ("t", 0.5), ["u"], "   ", {"text": ""}],
                                    lambda passages, max_chars: "|".join(passages))
        self.assertEqual(pipe.run("q", ["d"]).passages, ("s", "m", "t", "u"))

    def test_bad_passages(self):
        for bad in ([5], [("x",), 1], [[5]], [{"text": 5}]):
            pipe = rp.RetrievalPipeline(lambda q, d, top_k, bad=bad: bad, build)
            with self.assertRaises(TypeError):
                pipe.run("q", ["d"])

    def test_empty_results(self):
        for found in ([], None, ["  "]):
            pipe = rp.RetrievalPipeline(lambda q, d, top_k, f=found: f, build)
            with self.assertRaises(ValueError):
                pipe.run("q", ["d"])
        quiet = rp.RetrievalPipeline(lambda q, d, top_k: [], build, on_empty="empty")
        self.assertEqual((quiet.run("q", ["d"]).context, quiet.run("q", ["d"]).passages), ("", ()))

    def test_empty_context(self):
        strict = rp.RetrievalPipeline(lambda q, d, top_k: ["a"], lambda p, max_chars: "  ")
        with self.assertRaises(ValueError):
            strict.run("q", ["d"])
        lenient = rp.RetrievalPipeline(lambda q, d, top_k: ["a"], lambda p, max_chars: "", on_empty="empty")
        self.assertEqual(lenient.run("q", ["d"]).passages, ("a",))
        with self.assertRaises(TypeError):
            rp.RetrievalPipeline(lambda q, d, top_k: ["a"], lambda p, max_chars: 5).run("q", ["d"])

    def test_input_validation(self):
        pipe = rp.RetrievalPipeline(retrieve, build)
        for query in (5, None):
            with self.assertRaises(TypeError):
                pipe.run(query, DOCS)
        with self.assertRaises(ValueError):
            pipe.run("  ", DOCS)
        for docs in ("string", b"bytes", None, {"a"}, [1]):
            with self.assertRaises(TypeError):
                pipe.run("python", docs)

    def test_constructor_validation(self):
        for kwargs in ({"top_k": 0}, {"max_chars": -1}, {"on_empty": "ignore"}):
            with self.assertRaises(ValueError):
                rp.RetrievalPipeline(retrieve, build, **kwargs)
        for kwargs in ({"top_k": True}, {"max_chars": "5"}, {"rewrite_query": 5}):
            with self.assertRaises(TypeError):
                rp.RetrievalPipeline(retrieve, build, **kwargs)
        with self.assertRaises(TypeError):
            rp.RetrievalPipeline("x", build)
        with self.assertRaises(TypeError):
            rp.RetrievalPipeline(retrieve, "x")

    def test_rewrite_must_return_text(self):
        pipe = rp.RetrievalPipeline(retrieve, build, rewrite_query=lambda q: "")
        with self.assertRaises(ValueError):
            pipe.run("python", DOCS)

    def test_adapter_errors_propagate(self):
        def boom(q, d, top_k):
            raise RuntimeError("index offline")

        with self.assertRaisesRegex(RuntimeError, "index offline"):
            rp.RetrievalPipeline(boom, build).run("q", ["d"])

    def test_result_is_immutable(self):
        result = rp.RetrievalPipeline(retrieve, build).run("python", DOCS)
        with self.assertRaises(Exception):
            result.context = "x"


if __name__ == "__main__":
    unittest.main()
