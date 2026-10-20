# conversation-memory

**Version 1.1.0** · Python 3.9+ · standard library only · MIT

A small in-process conversation store for chat applications: add messages, keep the last N, search by keyword, fit recent history into a character budget, and export or restore a snapshot.

## Install

```bash
ai add conversation-memory@1.1.0
```

## Quick start

```python
from conversation_memory import ConversationMemory

memory = ConversationMemory(max_messages=100)
memory.add("user", "My favourite language is Python.")
memory.add("assistant", "Noted: Python.")

memory.recent(5)                      # newest 5 messages, oldest first
memory.search("python language")      # best keyword matches first
memory.window(max_chars=2000)         # [{"role", "content"}, ...] that fits the budget

snapshot = memory.to_dict()           # JSON-serializable
restored = ConversationMemory.from_dict(snapshot)
```

## API

| Method | Description |
|---|---|
| `ConversationMemory(max_messages=None, *, clock=time.time)` | Optional size limit; `clock` is injectable for tests. |
| `.add(role, content)` | Append a message; returns a copy with `id`, `role`, `content`, `time`. |
| `.extend(messages)` | Add many `{"role", "content"}` mappings. |
| `.recent(n=10)` | Newest `n` messages in chronological order. |
| `.search(query, limit=5)` | Messages sharing words with the query, best match first, ties newest first. |
| `.window(max_chars)` | Newest messages fitting a character budget, oldest first, as `{"role", "content"}`. |
| `.to_list()` | `{"role", "content"}` list for sending to a model. |
| `.to_dict()` / `ConversationMemory.from_dict(data)` | Snapshot and restore. |
| `.clear()`, `len(memory)`, `iter(memory)` | Housekeeping and iteration (yields copies). |

## Behavior

- Message ids increase monotonically and are never reused, even after trimming or `clear()`.
- Returned messages are copies; changing them does not change the store.
- Search is case-insensitive and Unicode-aware (letters and digits; underscores separate words).
- `role` must be a non-empty string and `content` a string, otherwise `ValueError`.
- This is in-memory only. To persist, store `to_dict()` yourself (for example as JSON).

## Changes in 1.1.0

Monotonic ids (fixes id reuse after trimming), copy-on-read, `window()`, `extend()`, `to_dict()`/`from_dict()`, Unicode-aware search, and an injectable clock.
