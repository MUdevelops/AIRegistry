# context-builder

**Version 1.1.0** · Python 3.9+ · standard library only · MIT

Turn retrieved passages into a numbered, size-limited context block for a prompt.

## Install

```bash
ai add context-builder@1.1.0
```

Optional: `ai add keyword-rag@1.1.0` if you want `build_context` to retrieve with the built-in keyword retriever.

## Quick start

```python
from context_builder import format_context, build_context

format_context(
    [{"id": "doc-1", "text": "AIRegistry installs reusable AI components."}, "Plain strings work too."],
    max_chars=500,
)
# <context>
# [1] (doc-1) AIRegistry installs reusable AI components.
# [2] Plain strings work too.
# </context>

# Retrieve and format in one call (uses keyword-rag if installed):
build_context("python language", ["Cats purr.", "Python is a language."], top_k=1)

# Or bring your own retriever:
build_context("q", docs, retrieve=lambda documents, query, top_k: my_search(query)[:top_k])
```

## API

| Function | Description |
|---|---|
| `format_context(results, max_chars=2000, header="context")` | Numbered block wrapped in `<header>` tags. |
| `build_context(query, documents, top_k=3, max_chars=2000, *, retrieve=None, header="context")` | Retrieve, then format. |

`results` items are strings, or mappings with a string `text` and optional `id` (the shape `keyword-rag` returns).

## Behavior

- `max_chars` is the budget for the numbered lines, including the newlines between them. The `<context>` wrapper tags are not counted.
- A passage that does not fit is cut with `...` when at least 24 characters remain; all later passages are dropped. If nothing fits, the result is `""`.
- Whitespace inside a passage is collapsed to single spaces.
- `header` must start with a letter and use only letters, digits, `_` or `-`; it is lowercased.
- A custom `retrieve` is called as `retrieve(documents, query, top_k)`.
- Without `retrieve`, `build_context` looks for `keyword_rag` on `sys.path` and then in the sibling install folder (`ai_components/keyword-rag/src`). If neither exists it raises `ImportError` with instructions.

## Changes in 1.1.0

Accepts plain-string passages, validates arguments, no longer modifies `sys.path`, supports a custom retriever and `header`, and makes the `max_chars` budget exact. `keyword-rag` is now optional rather than required.
