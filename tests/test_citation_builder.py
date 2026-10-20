import unittest

from _helpers import load_component

cb = load_component("citation-builder", "citation_builder")


class TestCitations(unittest.TestCase):
    full = {"title": "Notes", "author": "Ada Lovelace", "date": "1843", "url": "https://example.org/n"}

    def test_full_and_minimal_formats(self):
        self.assertEqual(cb.format_citation(1, self.full), "[1] Ada Lovelace. Notes (1843). https://example.org/n")
        self.assertEqual(cb.format_citation(2, {"title": "Only"}), "[2] Only.")

    def test_punctuation_and_whitespace(self):
        self.assertEqual(cb.format_citation(1, {"title": "Why?"}), "[1] Why?")
        self.assertEqual(cb.format_citation(1, {"title": "Done.", "author": "A."}), "[1] A. Done.")
        self.assertEqual(cb.format_citation(1, {"title": "  A   b \n c "}), "[1] A b c.")

    def test_validation(self):
        with self.assertRaises(ValueError):
            cb.format_citation(1, {"title": " "})
        with self.assertRaises(ValueError):
            cb.format_citation(0, {"title": "x"})
        with self.assertRaises(TypeError):
            cb.format_citation(1, "nope")

    def test_duplicates_merge_by_url_then_title(self):
        sources = [{"title": "A", "url": "https://x.org/a"}, {"title": "A copy", "url": "HTTPS://X.org/a/#top"},
                   {"title": "No url"}, {"title": "no  URL"}, {"title": "B", "url": "https://x.org/b"}]
        lines = cb.build_citations(sources)
        self.assertEqual(len(lines), 3)
        self.assertTrue(lines[2].startswith("[3] B"))

    def test_start_number(self):
        self.assertTrue(cb.build_citations([{"title": "A"}], start=5)[0].startswith("[5]"))

    def test_bibliography(self):
        text = cb.bibliography([{"title": "A"}, {"title": "B"}])
        self.assertEqual(text, "Sources\n[1] A.\n[2] B.")
        self.assertEqual(cb.bibliography([]), "")
        self.assertEqual(cb.bibliography([{"title": "A"}], heading=None), "[1] A.")

    def test_markers(self):
        self.assertEqual(cb.markers([3, 1, 3]), "[1][3]")
        self.assertEqual(cb.markers([]), "")
        for bad in ([0], [True], ["1"]):
            with self.assertRaises(ValueError):
                cb.markers(bad)

    def test_citation_index(self):
        index = cb.CitationIndex()
        self.assertEqual(index.add({"title": "A", "url": "https://a"}), 1)
        self.assertEqual(index.add({"title": "B"}), 2)
        self.assertEqual(index.add({"title": "A again", "url": "https://a/"}), 1)
        self.assertEqual(len(index), 2)
        self.assertEqual(index.citations(), ["[1] A. https://a", "[2] B."])
        self.assertIn("Sources", index.bibliography())
        self.assertEqual(cb.CitationIndex(10).add({"title": "x"}), 10)
        with self.assertRaises(ValueError):
            cb.CitationIndex(0)


if __name__ == "__main__":
    unittest.main()
