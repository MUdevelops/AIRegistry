# query-rewriter

**Version 1.1.0** · Python 3.9+ · standard library only · MIT

Deterministic query cleanup for retrieval workflows: normalize whitespace and Unicode, optionally drop stopwords or cap length, and derive keyword variants for multi-query search. No network, no model, no randomness.

## Install

```bash
ai add query-rewriter@1.1.0
```

## Quick start

```python
from query_rewriter import normalize_query, rewrite_query, extract_keywords, query_variants

normalize_query("  best   way to build\n a reusable   RAG system  ")
# 'best way to build a reusable RAG system'

rewrite_query("What is the best way to build a RAG system?", remove_stopwords=True, lowercase=True)
# 'best way build rag system?'

extract_keywords("What is the best way to build a RAG system?")
# ['best', 'way', 'build', 'rag', 'system']

query_variants("What is the best way to build a RAG system?")
# ['What is the best way to build a RAG system?', 'best way build rag system']
```

## API

| Function | Description |
|---|---|
| `normalize_query(query)` | NFKC normalization, control characters removed, whitespace collapsed. Wording and case are preserved. |
| `rewrite_query(query, *, lowercase=False, remove_stopwords=False, max_words=None)` | Normalize, then optionally lowercase, drop stopwords and cap the word count. |
| `extract_keywords(query, *, min_length=2, limit=None)` | Lowercase, de-duplicated keywords in first-seen order, without stopwords. |
| `query_variants(query, *, keywords=True)` | Distinct forms for multi-query retrieval: normalized query, then keyword form. |
| `STOPWORDS` | The English stopword set used by the functions above. |

## Behavior

- Pure functions of their input: the same query always gives the same result.
- `remove_stopwords=True` never empties a non-empty query; if every word is a stopword the normalized query is returned.
- Non-string input raises `TypeError`; invalid limits raise `ValueError`.
- Stopwords are English only. Other languages are normalized but not filtered.

## Pairs well with

`keyword-rag` (retrieve with the rewritten query) and `retrieval-pipeline` (pass `rewrite_query=` to apply it before retrieval).

## Changes in 1.1.0

First working release of this component. The 1.0.0 release imported a module it did not ship and has been withdrawn. 1.1.0 ships `query_rewriter.py` with the full API above.
