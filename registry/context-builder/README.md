# context-builder

Combine retrieved passages into a structured, size-limited context block for prompts.

## Install

```bash
ai add context-builder
```

Python standard library only.

## Dependencies

keyword-rag (`ai add keyword-rag`)

## API

`format_context(results, max_chars=2000, header="Context")` formats retrieved passages. `build_context(query, documents, top_k=3, max_chars=2000)` retrieves with the `keyword-rag` component first. Install it too: `ai add keyword-rag`.

## Example

```python
from context_builder import build_context

print(build_context("python", ["Python is a language", "Cats purr"], top_k=1))
```
