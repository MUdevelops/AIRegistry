"""conversation-memory: a small in-process conversation store.

Keeps chat messages in memory with optional size limit, keyword search,
recent-history and character-budget windows, and JSON-friendly export/import.
Standard library only. Python 3.9+.
"""
from __future__ import annotations

import re
import time
from typing import Any, Callable, Dict, Iterable, Iterator, List, Mapping, Optional

__all__ = ["ConversationMemory", "__version__"]
__version__ = "1.1.0"

Message = Dict[str, Any]

_WORDS = re.compile(r"[^\W_]+")


def _words(text: str) -> set:
    return set(_WORDS.findall(text.casefold()))


def _positive(name: str, value: Any) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return value


class ConversationMemory:
    """Ordered store of ``{"id", "role", "content", "time"}`` messages.

    Args:
        max_messages: Keep only the newest N messages (``None`` keeps everything).
        clock: Function returning the current time in seconds; override in tests.
    """

    def __init__(
        self,
        max_messages: Optional[int] = None,
        *,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self.max_messages = None if max_messages is None else _positive("max_messages", max_messages)
        self._clock = clock
        self._messages: List[Message] = []
        self._next_id = 0

    # -- writing -----------------------------------------------------------
    def add(self, role: str, content: str) -> Message:
        """Append a message and return a copy of it. Ids increase monotonically, even after trimming."""
        if not isinstance(role, str) or not role.strip():
            raise ValueError("role must be a non-empty string")
        if not isinstance(content, str):
            raise ValueError("content must be a string")
        message = {"id": self._next_id, "role": role.strip(), "content": content, "time": self._clock()}
        self._next_id += 1
        self._messages.append(message)
        if self.max_messages is not None and len(self._messages) > self.max_messages:
            del self._messages[: len(self._messages) - self.max_messages]
        return dict(message)

    def extend(self, messages: Iterable[Mapping[str, Any]]) -> None:
        """Add many ``{"role", "content"}`` mappings in order."""
        for item in messages:
            self.add(item["role"], item["content"])

    def clear(self) -> None:
        """Remove all messages. Ids keep increasing afterwards."""
        self._messages = []

    # -- reading -----------------------------------------------------------
    def recent(self, n: int = 10) -> List[Message]:
        """The newest ``n`` messages in chronological order (empty for ``n <= 0``)."""
        if n <= 0:
            return []
        return [dict(m) for m in self._messages[-n:]]

    def search(self, query: str, limit: int = 5) -> List[Message]:
        """Messages sharing words with ``query``, best match first (ties: newest first)."""
        terms = _words(query)
        if not terms or limit <= 0:
            return []
        hits = []
        for m in self._messages:
            score = len(terms & _words(m["content"]))
            if score:
                hits.append((score, m))
        hits.sort(key=lambda pair: (-pair[0], -pair[1]["id"]))
        return [dict(m) for _, m in hits[:limit]]

    def window(self, max_chars: int) -> List[Dict[str, str]]:
        """Newest messages whose combined content fits in ``max_chars``, oldest first.

        Returns ``{"role", "content"}`` dicts ready to send to a chat model. The newest
        message is always the first one considered; the window stops at the first message
        that does not fit.
        """
        _positive("max_chars", max_chars)
        picked: List[Dict[str, str]] = []
        used = 0
        for m in reversed(self._messages):
            used += len(m["content"])
            if used > max_chars:
                break
            picked.append({"role": m["role"], "content": m["content"]})
        picked.reverse()
        return picked

    # -- export / import ---------------------------------------------------
    def to_list(self) -> List[Dict[str, str]]:
        """Messages as ``{"role", "content"}`` dicts."""
        return [{"role": m["role"], "content": m["content"]} for m in self._messages]

    def to_dict(self) -> Dict[str, Any]:
        """A JSON-serializable snapshot, restorable with :meth:`from_dict`."""
        return {
            "max_messages": self.max_messages,
            "next_id": self._next_id,
            "messages": [dict(m) for m in self._messages],
        }

    @classmethod
    def from_dict(
        cls, data: Mapping[str, Any], *, clock: Callable[[], float] = time.time
    ) -> "ConversationMemory":
        """Rebuild a store from :meth:`to_dict` output."""
        memory = cls(data.get("max_messages"), clock=clock)
        for raw in data.get("messages", []):
            message = {
                "id": int(raw["id"]), "role": str(raw["role"]),
                "content": str(raw["content"]), "time": float(raw["time"]),
            }
            memory._messages.append(message)
        highest = max((m["id"] for m in memory._messages), default=-1)
        memory._next_id = max(int(data.get("next_id", 0)), highest + 1)
        if memory.max_messages is not None and len(memory._messages) > memory.max_messages:
            del memory._messages[: len(memory._messages) - memory.max_messages]
        return memory

    # -- container protocol ------------------------------------------------
    def __len__(self) -> int:
        return len(self._messages)

    def __iter__(self) -> Iterator[Message]:
        return (dict(m) for m in self._messages)
