# retrieval-pipeline

**Version 1.1.0** · Python 3.9+ · standard library only · MIT

Compose retrieval and context building into one validated workflow that produces bounded, prompt-ready context. It is adapter based, so it works with any retriever and any context formatter.

```text
query -> [rewrite] -> retrieve -> normalize passages -> build context -> RetrievalResult
```

## Install

```bash
ai add retrieval-pipeline@1.1.0
```

The pipeline itself has no dependencies. The example below uses these optional components:

```bash
ai add keyword-rag@1.1.0
ai add context-builder@1.1.0
ai add query-rewriter@1.1.0
```

## Quick start

```python
from keyword_rag import retrieve as keyword_retrieve
from context_builder import format_context
from query_rewriter import rewrite_query
from retrieval_pipeline import RetrievalPipeline

pipeline = RetrievalPipeline(
    retrieve=lambda query, documents, top_k: keyword_retrieve(documents, query, top_k),
    build_context=lambda passages, max_chars: format_context(passages, max_chars),
    top_k=3,
    max_chars=2000,
    rewrite_query=lambda q: rewrite_query(q, remove_stopwords=True),
)

documents = ["Cats purr when happy.", "Python is a programming language.", "AIRegistry installs components."]
result = pipeline.run("What is the Python language?", documents)

print(result.context)      # <context>\n[1] Python is a programming language.\n</context>
print(result.passages)     # ('Python is a programming language.',)
```

## API

`RetrievalPipeline(retrieve, build_context, *, top_k=5, max_chars=4000, rewrite_query=None, on_empty="raise")`

| Member | Description |
|---|---|
| `.run(query, documents)` (also `pipeline(query, documents)`) | Returns a `RetrievalResult`. |
| `RetrievalResult` | Frozen dataclass: `query`, `retrieval_query`, `passages` (tuple of strings), `context`; `.to_dict()`. |
| `build_retrieval_context(query, documents, *, retrieve, build_context, top_k=5, max_chars=4000)` | One-call form returning only the context string. |

### Adapter contracts

- `retrieve(query, documents, top_k=top_k)` returns passages as strings, mappings with a `text` key, or sequences whose first item is the text.
- `build_context(passages, max_chars=max_chars)` receives a list of passage strings and returns a string.
- `rewrite_query(query)` (optional) returns the query to use for retrieval.

## Behavior and errors

- The query must be a non-empty string; `documents` must be a sequence (not a single string) of strings. Wrong types raise `TypeError`, empty queries raise `ValueError`.
- Passages are stripped and empty ones dropped.
- When nothing usable is retrieved, or the builder returns empty context, `ValueError` is raised. Use `on_empty="empty"` to get a result with `context == ""` instead.
- `top_k` and `max_chars` must be positive integers.
- Failures raised by your adapters propagate unchanged.

## Changes in 1.1.0

The 1.0.0 source file contained a stray markdown fence and could not be imported, so that release has been withdrawn. 1.1.0 adds `RetrievalPipeline`, `RetrievalResult`, optional query rewriting and `on_empty`, and keeps `build_retrieval_context` from 1.0.0.
