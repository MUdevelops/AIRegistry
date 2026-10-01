"""JSON-file memory store."""
import json
import os


class Memory:
    def __init__(self, path="memory.json"):
        self.path, self.items = path, []
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                self.items = json.load(f)

    def add(self, text):
        self.items.append(text)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.items, f)

    def search(self, q):
        return [t for t in self.items if q.lower() in t.lower()]
