import json
import unittest

from _helpers import load_component

cm = load_component("conversation-memory", "conversation_memory")


class Clock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        self.t += 1
        return self.t


class TestMemory(unittest.TestCase):
    def make(self, **kw):
        return cm.ConversationMemory(clock=Clock(), **kw)

    def test_add_returns_copy_with_metadata(self):
        m = self.make()
        msg = m.add("user", "hello")
        self.assertEqual((msg["id"], msg["role"], msg["content"], msg["time"]), (0, "user", "hello", 1.0))
        msg["content"] = "changed"
        self.assertEqual(m.recent()[0]["content"], "hello")

    def test_validation(self):
        m = self.make()
        for role, content in (("", "x"), ("  ", "x"), (None, "x"), ("user", 5), ("user", None)):
            with self.assertRaises(ValueError):
                m.add(role, content)
        for bad in (0, -1, True, "5"):
            with self.assertRaises(ValueError):
                cm.ConversationMemory(bad)

    def test_trimming_keeps_newest_and_ids_never_repeat(self):
        m = self.make(max_messages=3)
        for i in range(6):
            m.add("user", f"m{i}")
        self.assertEqual([x["id"] for x in m.recent(10)], [3, 4, 5])
        self.assertEqual(len(m), 3)
        m.clear()
        self.assertEqual(m.add("user", "again")["id"], 6)

    def test_recent(self):
        m = self.make()
        for i in range(5):
            m.add("user", str(i))
        self.assertEqual([x["content"] for x in m.recent(2)], ["3", "4"])
        self.assertEqual(m.recent(0), [])
        self.assertEqual(m.recent(-1), [])

    def test_search_ranks_by_overlap_then_recency(self):
        m = self.make()
        m.add("user", "python is great")
        m.add("user", "I like python and cats")
        m.add("user", "python")
        m.add("user", "unrelated")
        hits = m.search("python cats")
        self.assertEqual([h["id"] for h in hits], [1, 2, 0])
        self.assertEqual(m.search(""), [])
        self.assertEqual(m.search("python", limit=1)[0]["id"], 2)
        self.assertEqual(m.search("python", limit=0), [])

    def test_search_is_case_and_unicode_aware(self):
        m = self.make()
        m.add("user", "Café Zürich")
        self.assertEqual(len(m.search("CAFÉ")), 1)
        m.add("user", "snake_case")
        self.assertEqual(len(m.search("case")), 1)

    def test_window_fits_budget_newest_first_selection(self):
        m = self.make()
        for text in ("aaaa", "bbbb", "cccc"):
            m.add("user", text)
        self.assertEqual([x["content"] for x in m.window(8)], ["bbbb", "cccc"])
        self.assertEqual(m.window(3), [])
        self.assertEqual(len(m.window(1000)), 3)
        with self.assertRaises(ValueError):
            m.window(0)

    def test_extend_and_to_list(self):
        m = self.make()
        m.extend([{"role": "user", "content": "a"}, {"role": "assistant", "content": "b"}])
        self.assertEqual(m.to_list(), [{"role": "user", "content": "a"}, {"role": "assistant", "content": "b"}])
        self.assertEqual([x["role"] for x in m], ["user", "assistant"])

    def test_snapshot_round_trip_through_json(self):
        m = self.make(max_messages=5)
        for i in range(8):
            m.add("user", f"m{i}")
        restored = cm.ConversationMemory.from_dict(json.loads(json.dumps(m.to_dict())), clock=Clock())
        self.assertEqual(restored.to_list(), m.to_list())
        self.assertEqual(restored.max_messages, 5)
        self.assertEqual(restored.add("user", "next")["id"], 8)

    def test_iteration_yields_copies(self):
        m = self.make()
        m.add("user", "x")
        for item in m:
            item["content"] = "changed"
        self.assertEqual(m.recent()[0]["content"], "x")


if __name__ == "__main__":
    unittest.main()
