"""keyword-rag: dependency-free keyword retrieval over a list of documents.

Documents are ranked with a TF-IDF style score computed from a simple tokenizer
(letters and digits, lowercase, common English stopwords removed). It is meant
for small corpora, prototypes and tests; for large corpora use a vector index.
Standard library only. Python 3.9+.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Union

__all__ = ["STOPWORDS", "tokenize", "retrieve", "KeywordRetriever", "__version__"]
__version__ = "1.1.0"

STOPWORDS = frozenset(
    "a an and are as at be by for from has in is it of on or that the to was were with".split()
)

_TOKEN = re.compile(r"[^\W_]+")

Document = Union[str, Mapping[str, Any]]


def tokenize(text: str) -> List[str]:
    """Lowercase ``text`` into word tokens, dropping stopwords."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    return [t for t in _TOKEN.findall(text.casefold()) if t not in STOPWORDS]


def _top_k(value: Any) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError("top_k must be an integer")
    if value < 1:
        raise ValueError("top_k must be >= 1")
    return value


def _normalize(documents: Iterable[Document]) -> List[Dict[str, Any]]:
    if isinstance(documents, (str, bytes)):
        raise TypeError("documents must be a list of strings or {'id', 'text'} mappings")
    docs: List[Dict[str, Any]] = []
    for position, item in enumerate(documents):
        if isinstance(item, str):
            doc_id, text = position, item
        elif isinstance(item, Mapping) and isinstance(item.get("text"), str):
            doc_id, text = item.get("id", position), item["text"]
        else:
            raise TypeError(f"document {position} must be a string or a mapping with a string 'text'")
        docs.append({"id": doc_id, "text": text, "counts": Counter(tokenize(text))})
    return docs


def retrieve(documents: Iterable[Document], query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Return up to ``top_k`` results ranked by relevance to ``query``.

    Args:
        documents: Strings or ``{"id": ..., "text": ...}`` mappings. A string's id is its position.
        query: Search text. Only terms that appear in a document contribute to its score.
        top_k: Maximum number of results (>= 1).

    Returns:
        A list of ``{"id", "score", "text"}`` dicts, best first. Equal scores keep input order.
        Documents with no matching term are never returned.
    """
    if not isinstance(query, str):
        raise TypeError("query must be a string")
    limit = _top_k(top_k)
    docs = _normalize(documents)
    terms = set(tokenize(query))
    if not docs or not terms:
        return []
    total = len(docs)
    doc_freq = {t: sum(1 for d in docs if t in d["counts"]) for t in terms}
    ranked = []
    for position, d in enumerate(docs):
        score = 0.0
        for term in terms:
            tf = d["counts"].get(term, 0)
            if tf:
                score += (1 + math.log(tf)) * (math.log((total + 1) / doc_freq[term]) + 1)
        if score > 0:
            ranked.append((-score, position, {"id": d["id"], "score": round(score, 4), "text": d["text"]}))
    ranked.sort(key=lambda row: (row[0], row[1]))
    return [row[2] for row in ranked[:limit]]


class KeywordRetriever:
    """A growing document collection with a :meth:`retrieve` method."""

    def __init__(self, documents: Optional[Iterable[Document]] = None) -> None:
        self.documents: List[Dict[str, Any]] = []
        if documents is not None:
            self.add_documents(documents)

    def add_document(self, text: str, id: Any = None) -> Any:  # noqa: A002 - public parameter name
        """Add one document and return its id (its position when ``id`` is omitted)."""
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        doc_id = len(self.documents) if id is None else id
        self.documents.append({"id": doc_id, "text": text})
        return doc_id

    def add_documents(self, documents: Iterable[Document]) -> None:
        """Add several strings or ``{"id", "text"}`` mappings."""
        if isinstance(documents, (str, bytes)):
            raise TypeError("documents must be a list of strings or {'id', 'text'} mappings")
        for position, item in enumerate(documents):
            if isinstance(item, str):
                self.add_document(item)
            elif isinstance(item, Mapping) and isinstance(item.get("text"), str):
                self.add_document(item["text"], item.get("id"))
            else:
                raise TypeError(f"document {position} must be a string or a mapping with a string 'text'")

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Rank the stored documents for ``query``."""
        return retrieve(self.documents, query, top_k)

    def clear(self) -> None:
        """Remove all documents."""
        self.documents = []

    def __len__(self) -> int:
        return len(self.documents)
