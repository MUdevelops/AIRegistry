# keyword-rag

Lightweight keyword retrieval over documents, returning ranked relevant context.

## Install

```bash
ai add keyword-rag
```

Python standard library only.

## API

`retrieve(documents, query, top_k=3)` returns ranked `{id, score, text}` dicts. `KeywordRetriever` offers `.add_document(text, id=None)` and `.retrieve(query, top_k)`. Documents may be strings or `{id, text}` dicts.

## Example

```python
from keyword_rag import retrieve

docs = ["Cats purr when happy", "Python is a programming language"]
print(retrieve(docs, "python language", top_k=1))
```
