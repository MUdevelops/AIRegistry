import unittest

from _helpers import load_component

kr = load_component("keyword-rag", "keyword_rag")
old = load_component("keyword-rag", "keyword_rag", "1.0.0")

DOCS = ["Cats purr when they are happy", "Python is a programming language",
        "Python and cats and python", "Dogs bark loudly", {"id": "faq", "text": "Install python with the ai CLI"}]


class TestRetrieve(unittest.TestCase):
    def test_ranks_and_shapes_results(self):
        res = kr.retrieve(DOCS, "python language", top_k=2)
        self.assertEqual([r["id"] for r in res], [1, 2])
        self.assertEqual(set(res[0]), {"id", "score", "text"})
        self.assertGreater(res[0]["score"], res[1]["score"])

    def test_no_match_returns_empty(self):
        self.assertEqual(kr.retrieve(DOCS, "zebra"), [])
        self.assertEqual(kr.retrieve([], "python"), [])
        self.assertEqual(kr.retrieve(DOCS, "the of and"), [])

    def test_mapping_ids_are_preserved(self):
        self.assertEqual(kr.retrieve(DOCS, "install cli")[0]["id"], "faq")

    def test_ties_keep_input_order(self):
        res = kr.retrieve(["alpha beta", "alpha gamma", "alpha delta"], "alpha", top_k=3)
        self.assertEqual([r["id"] for r in res], [0, 1, 2])

    def test_top_k_limits_and_validates(self):
        self.assertEqual(len(kr.retrieve(DOCS, "python", top_k=1)), 1)
        with self.assertRaises(ValueError):
            kr.retrieve(DOCS, "python", top_k=0)
        for bad in (True, "3", 1.5):
            with self.assertRaises(TypeError):
                kr.retrieve(DOCS, "python", top_k=bad)

    def test_input_validation(self):
        with self.assertRaises(TypeError):
            kr.retrieve("one big string", "x")
        with self.assertRaises(TypeError):
            kr.retrieve([5], "x")
        with self.assertRaises(TypeError):
            kr.retrieve([{"id": 1}], "x")
        with self.assertRaises(TypeError):
            kr.retrieve(DOCS, None)

    def test_tokenizer(self):
        self.assertEqual(kr.tokenize("The Cat's snake_case-2 CAFÉ"), ["cat", "s", "snake", "case", "2", "café"])
        with self.assertRaises(TypeError):
            kr.tokenize(None)

    def test_scores_match_1_0_0(self):
        for query in ("python language", "cats", "python cats", "dogs bark", "zzz"):
            self.assertEqual(kr.retrieve(DOCS[:4], query, 3), old.retrieve(DOCS[:4], query, 3), query)

    def test_input_not_mutated(self):
        docs = [{"id": 1, "text": "python"}]
        kr.retrieve(docs, "python")
        self.assertEqual(docs, [{"id": 1, "text": "python"}])


class TestRetriever(unittest.TestCase):
    def test_add_and_retrieve(self):
        store = kr.KeywordRetriever()
        self.assertEqual(store.add_document("hello world"), 0)
        self.assertEqual(store.add_document("goodbye world", id="g"), "g")
        store.add_documents(["third doc", {"id": "x", "text": "fourth world"}])
        self.assertEqual(len(store), 4)
        self.assertEqual({r["id"] for r in store.retrieve("world", 5)}, {0, "g", "x"})
        store.clear()
        self.assertEqual(len(store), 0)

    def test_constructor_documents_and_validation(self):
        self.assertEqual(len(kr.KeywordRetriever(["a b", "c d"])), 2)
        with self.assertRaises(TypeError):
            kr.KeywordRetriever().add_document(5)
        with self.assertRaises(TypeError):
            kr.KeywordRetriever().add_documents("abc")
        with self.assertRaises(TypeError):
            kr.KeywordRetriever().add_documents([5])


if __name__ == "__main__":
    unittest.main()
