"""conversation-memory: small local in-memory conversation store."""
import re
import time


def _words(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))


class ConversationMemory:
    def __init__(self, max_messages=None):
        self.max_messages = max_messages
        self.messages = []

    def add(self, role, content):
        if not role or not isinstance(content, str):
            raise ValueError("role and string content are required")
        msg = {"id": len(self.messages) and self.messages[-1]["id"] + 1, "role": role,
               "content": content, "time": time.time()}
        self.messages.append(msg)
        if self.max_messages and len(self.messages) > self.max_messages:
            del self.messages[:len(self.messages) - self.max_messages]
        return msg

    def recent(self, n=10):
        return self.messages[-n:] if n > 0 else []

    def search(self, query, limit=5):
        """Return messages sharing words with query, best match first (ties: newest first)."""
        q = _words(query)
        scored = [(len(q & _words(m["content"])), m) for m in self.messages]
        hits = [(s, m) for s, m in scored if s]
        hits.sort(key=lambda x: (-x[0], -x[1]["id"]))
        return [m for _, m in hits[:limit]]

    def clear(self):
        self.messages = []

    def to_list(self):
        return [{"role": m["role"], "content": m["content"]} for m in self.messages]

    def __len__(self):
        return len(self.messages)
