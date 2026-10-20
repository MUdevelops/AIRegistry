import unittest

from _helpers import load_component

qr = load_component("query-rewriter", "query_rewriter")


class TestQueryRewriter(unittest.TestCase):
    def test_normalize_whitespace_controls_and_unicode(self):
        self.assertEqual(qr.normalize_query("  best   way\n to\tbuild \u200b RAG  "), "best way to build RAG")
        self.assertEqual(qr.normalize_query("\ufb01nd \uff21\uff22"), "find AB")
        self.assertEqual(qr.normalize_query("a\x00b"), "a b")
        self.assertEqual(qr.normalize_query("   "), "")
        self.assertEqual(qr.normalize_query(""), "")

    def test_preserves_case_and_wording(self):
        self.assertEqual(qr.rewrite_query("  Why IS Python Great? "), "Why IS Python Great?")

    def test_options(self):
        q = "What is the best way to build a RAG system?"
        self.assertEqual(qr.rewrite_query(q, lowercase=True), q.lower())
        self.assertEqual(qr.rewrite_query(q, remove_stopwords=True), "best way build RAG system?")
        self.assertEqual(qr.rewrite_query(q, max_words=3), "What is the")
        self.assertEqual(qr.rewrite_query(q, remove_stopwords=True, max_words=2, lowercase=True), "best way")

    def test_stopword_removal_never_empties_a_query(self):
        self.assertEqual(qr.rewrite_query("the of and", remove_stopwords=True), "the of and")
        self.assertEqual(qr.rewrite_query("", remove_stopwords=True), "")

    def test_punctuated_stopwords_are_recognised(self):
        self.assertEqual(qr.rewrite_query("\u201cthe\u201d cat,", remove_stopwords=True), "cat,")

    def test_keywords(self):
        self.assertEqual(qr.extract_keywords("What is the best way to build a RAG system? Build it!"),
                         ["best", "way", "build", "rag", "system"])
        self.assertEqual(qr.extract_keywords("a bb ccc", min_length=3), ["ccc"])
        self.assertEqual(qr.extract_keywords("alpha beta gamma", limit=2), ["alpha", "beta"])
        self.assertEqual(qr.extract_keywords("don't stop"), ["don't", "stop"])
        self.assertEqual(qr.extract_keywords(""), [])

    def test_variants(self):
        self.assertEqual(qr.query_variants("What is the best way to build a RAG system?"),
                         ["What is the best way to build a RAG system?", "best way build rag system"])
        self.assertEqual(qr.query_variants("python"), ["python"])
        self.assertEqual(qr.query_variants("Python"), ["Python"])
        self.assertEqual(qr.query_variants("the of"), ["the of"])
        self.assertEqual(qr.query_variants("  "), [])
        self.assertEqual(qr.query_variants("what is python", keywords=False), ["what is python"])

    def test_validation(self):
        for fn in (qr.normalize_query, qr.rewrite_query, qr.extract_keywords, qr.query_variants):
            with self.assertRaises(TypeError):
                fn(None)
        for bad in (0, -1, True, "2"):
            with self.assertRaises(ValueError):
                qr.rewrite_query("x", max_words=bad)
            with self.assertRaises(ValueError):
                qr.extract_keywords("x", min_length=bad)
            with self.assertRaises(ValueError):
                qr.extract_keywords("x", limit=bad)

    def test_is_deterministic(self):
        q = "How do I build a retrieval pipeline for my docs?"
        self.assertEqual({qr.rewrite_query(q, remove_stopwords=True) for _ in range(20)}, {qr.rewrite_query(q, remove_stopwords=True)})


if __name__ == "__main__":
    unittest.main()
