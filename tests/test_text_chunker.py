import unittest

from _helpers import load_component

tc = load_component("text-chunker", "text_chunker")
old = load_component("text-chunker", "text_chunker", "1.0.0")


class TestChunker(unittest.TestCase):
    def test_char_chunks_with_overlap(self):
        self.assertEqual(tc.chunk_text("abcdefghij", 4, 1), ["abcd", "defg", "ghij"])

    def test_word_chunks(self):
        self.assertEqual(tc.chunk_text("a b c d e", 3, 1, "words"), ["a b c", "c d e"])
        self.assertEqual(tc.chunk_text("a  b\nc", 2, 0, "words"), ["a b", "c"])

    def test_empty_and_short_inputs(self):
        self.assertEqual(tc.chunk_text("", 3, 1), [])
        self.assertEqual(tc.chunk_text("   ", 3, 1, "words"), [])
        self.assertEqual(tc.chunk_text("ab", 10, 2), ["ab"])

    def test_last_chunk_reaches_the_end_without_duplicates(self):
        for n in range(1, 40):
            text = "x" * n
            chunks = tc.chunk_text(text, 7, 3)
            self.assertTrue(chunks[-1].endswith("x"))
            self.assertEqual(len(chunks[-1]) <= 7, True)
            self.assertEqual(len(set((s["start"] for s in tc.chunk_with_offsets(text, 7, 3)))), len(chunks))

    def test_offsets_slice_back_to_the_source(self):
        text = "The quick  brown fox\njumps over the lazy dog"
        for by in ("chars", "words"):
            for item in tc.chunk_with_offsets(text, 5, 2, by):
                self.assertEqual(text[item["start"]:item["end"]], item["text"])
        self.assertEqual(tc.chunk_with_offsets("abcdef", 4, 2)[1],
                         {"index": 1, "start": 2, "end": 6, "text": "cdef"})

    def test_iter_chunks_is_lazy_and_equal(self):
        it = tc.iter_chunks("abcdefghij", 4, 1)
        self.assertEqual(next(it), "abcd")
        self.assertEqual(list(tc.iter_chunks("abcdefghij", 4, 1)), tc.chunk_text("abcdefghij", 4, 1))

    def test_validation(self):
        for args in ((("abc", 0, 0)), ("abc", 2, 2), ("abc", 2, -1), ("abc", 2, 0, "lines")):
            with self.assertRaises(ValueError):
                tc.chunk_text(*args)
        for args in ((5, 2, 0), ("abc", 2.5, 0), ("abc", True, 0), ("abc", 3, "1")):
            with self.assertRaises(TypeError):
                tc.chunk_text(*args)

    def test_same_output_as_1_0_0(self):
        text = "lorem ipsum dolor sit amet consectetur " * 5
        for size, overlap, by in ((10, 3, "chars"), (4, 1, "words"), (1, 0, "chars")):
            self.assertEqual(tc.chunk_text(text, size, overlap, by), old.chunk_text(text, size, overlap, by))


if __name__ == "__main__":
    unittest.main()
