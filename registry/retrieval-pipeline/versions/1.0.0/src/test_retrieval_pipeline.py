import unittest

from retrieval_pipeline import build_retrieval_context


class RetrievalPipelineTests(unittest.TestCase):
    def test_builds_context(self):
        def retrieve(query, documents, *, top_k):
            return documents[:top_k]

        def build_context(passages, *, max_chars):
            return "\n\n".join(passages)[:max_chars]

        result = build_retrieval_context(
            "AIRegistry",
            ["one", "two", "three"],
            retrieve=retrieve,
            build_context=build_context,
            top_k=2,
            max_chars=100,
        )

        self.assertEqual(result, "one\n\ntwo")

    def test_rejects_empty_query(self):
        with self.assertRaises(ValueError):
            build_retrieval_context(
                "   ",
                ["one"],
                retrieve=lambda *args, **kwargs: ["one"],
                build_context=lambda passages, **kwargs: passages[0],
            )

    def test_rejects_invalid_top_k(self):
        with self.assertRaises(ValueError):
            build_retrieval_context(
                "query",
                ["one"],
                retrieve=lambda *args, **kwargs: ["one"],
                build_context=lambda passages, **kwargs: passages[0],
                top_k=0,
            )

    def test_rejects_empty_retrieval_result(self):
        with self.assertRaises(ValueError):
            build_retrieval_context(
                "query",
                ["one"],
                retrieve=lambda *args, **kwargs: [],
                build_context=lambda passages, **kwargs: "unused",
            )

    def test_accepts_structured_passages(self):
        def retrieve(query, documents, *, top_k):
            return [{"text": "alpha"}, {"text": "beta"}][:top_k]

        def build_context(passages, *, max_chars):
            return " | ".join(passages)[:max_chars]

        result = build_retrieval_context(
            "query",
            ["alpha", "beta"],
            retrieve=retrieve,
            build_context=build_context,
            top_k=2,
        )

        self.assertEqual(result, "alpha | beta")


if __name__ == "__main__":
    unittest.main()