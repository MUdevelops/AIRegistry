# conversation-memory

Small local in-memory conversation store with add, search, recent and clear.

## Install

```bash
ai add conversation-memory
```

Python standard library only.

## API

`ConversationMemory(max_messages=None)` with `.add(role, content)`, `.recent(n)`, `.search(query, limit=5)`, `.clear()`, `.to_list()`. Data stays in process memory only.

## Example

```python
from conversation_memory import ConversationMemory

m = ConversationMemory()
m.add("user", "My favorite color is green")
print(m.search("favorite color"))
```
