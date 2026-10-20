"""query-rewriter: deterministic query cleanup for retrieval workflows.

Normalizes user search text (Unicode form, control characters, whitespace),
optionally lowercases it, drops stopwords or limits its length, and can derive
keyword and multi-query variants. No network, models or randomness.
Standard library only. Python 3.9+.
"""
from __future__ import annotations

import re
import string
import unicodedata
from typing import List, Optional

__all__ = ["normalize_query", "rewrite_query", "extract_keywords", "query_variants", "STOPWORDS", "__version__"]
__version__ = "1.1.0"

STOPWORDS = frozenset(
    """a about an and are as at be been but by can do does for from has have how i if in into is it its
    me my of on or our so than that the their them then there these they this to us was we were what when
    where which who why will with would you your""".split()
)

_SPACES = re.compile(r"\s+")
_TOKEN = re.compile(r"[^\W_]+(?:['\u2019][^\W_]+)*")


def _require_text(query: object) -> str:
    if not isinstance(query, str):
        raise TypeError("query must be a string")
    return query


def normalize_query(query: str) -> str:
    """Return ``query`` in NFKC form with control characters removed and whitespace collapsed.

    The wording and letter case are preserved. ``"  best   way\\n to build "`` becomes ``"best way to build"``.
    """
    text = unicodedata.normalize("NFKC", _require_text(query))
    text = "".join(ch if ch.isspace() or unicodedata.category(ch) not in ("Cc", "Cf") else " " for ch in text)
    return _SPACES.sub(" ", text).strip()


def _strip_word(word: str) -> str:
    return word.strip(string.punctuation + "\u2018\u2019\u201c\u201d").casefold()


def rewrite_query(
    query: str,
    *,
    lowercase: bool = False,
    remove_stopwords: bool = False,
    max_words: Optional[int] = None,
) -> str:
    """Normalize ``query`` and optionally lowercase it, drop stopwords and cap its length.

    Args:
        query: Raw user text.
        lowercase: Lowercase the result.
        remove_stopwords: Remove common English stopwords. If every word is a stopword the
            normalized query is kept, so a non-empty query never becomes empty.
        max_words: Keep at most this many words (must be >= 1).
    """
    text = normalize_query(query)
    if max_words is not None and (not isinstance(max_words, int) or isinstance(max_words, bool) or max_words < 1):
        raise ValueError("max_words must be a positive integer")
    words = text.split()
    if remove_stopwords:
        kept = [w for w in words if _strip_word(w) not in STOPWORDS]
        words = kept or words
    if max_words is not None:
        words = words[:max_words]
    text = " ".join(words)
    return text.lower() if lowercase else text


def extract_keywords(query: str, *, min_length: int = 2, limit: Optional[int] = None) -> List[str]:
    """Lowercase keywords in first-seen order, without stopwords, duplicates or short tokens."""
    if not isinstance(min_length, int) or isinstance(min_length, bool) or min_length < 1:
        raise ValueError("min_length must be a positive integer")
    if limit is not None and (not isinstance(limit, int) or isinstance(limit, bool) or limit < 1):
        raise ValueError("limit must be a positive integer")
    seen = set()
    keywords: List[str] = []
    for token in _TOKEN.findall(normalize_query(query).casefold()):
        if len(token) < min_length or token in STOPWORDS or token in seen:
            continue
        seen.add(token)
        keywords.append(token)
    return keywords[:limit] if limit else keywords


def query_variants(query: str, *, keywords: bool = True) -> List[str]:
    """Distinct query forms for multi-query retrieval, most faithful first.

    Returns the normalized query and, when ``keywords`` is true, the keyword-only form.
    An empty query gives ``[]``.
    """
    base = normalize_query(query)
    if not base:
        return []
    variants = [base]
    if keywords:
        compact = " ".join(extract_keywords(base))
        if compact and compact.casefold() != base.casefold():
            variants.append(compact)
    return variants
