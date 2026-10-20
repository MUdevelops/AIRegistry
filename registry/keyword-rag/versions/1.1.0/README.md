# keyword-rag

**Version 1.1.0** · Python 3.9+ · standard library only · MIT

Dependency-free keyword retrieval for small corpora: rank documents against a query with a TF-IDF style score and get the best passages back, ready for a prompt.

## Install

```bash
ai add keyword-rag@1.1.0
```

## Quick start

```python
from keyword_rag import retrieve, KeywordRetriever

docs = [
    "Cats purr when they are happy.",
    "Python is a programming language.",
    {"id": "faq-3", "text": "Use the ai CLI to add Python components."},
]

retrieve(docs, "python language", top_k=2)
# [{'id': 1, 'score': ..., 'text': 'Python is a programming language.'},
#  {'id': 'faq-3', 'score': ..., 'text': 'Use the ai CLI to add Python components.'}]

store = KeywordRetriever()
store.add_document("Chunk about retrieval", id="c1")
store.retrieve("retrieval")
```

## API

| Name | Description |
|---|---|
| `retrieve(documents, query, top_k=3)` | Returns up to `top_k` `{id, score, text}` dicts, best first. |
| `KeywordRetriever(documents=None)` | `.add_document(text, id=None)`, `.add_documents(items)`, `.retrieve(query, top_k=3)`, `.clear()`, `len(store)`. |
| `tokenize(text)` | The tokenizer used for documents and queries. |
| `STOPWORDS` | The built-in English stopword set. |

`documents` may contain plain strings (their id is their position) or mappings with a string `text` and an optional `id`.

## Behavior

- Tokens are lowercase letters and digits (Unicode-aware); a small set of English stopwords is ignored.
- Score = sum over query terms of `(1 + ln(tf)) * (ln((N + 1) / df) + 1)`, where `tf` is the term count in the document, `df` the number of documents containing it and `N` the corpus size.
- Documents with no matching term are never returned. Equal scores keep input order.
- Invalid input raises `TypeError` (wrong types) or `ValueError` (`top_k < 1`).
- Complexity is linear in corpus size per query. For large corpora use an inverted or vector index.

## Pairs well with

`context-builder` (formats results as a prompt block) and `retrieval-pipeline` (wires retrieval and context building together).

## Changes in 1.1.0

Document frequencies are computed once per query instead of once per document and term, tokenization is Unicode-aware, ties keep input order, and inputs are validated. Scores for existing inputs are unchanged.
