"""text-chunker: split text into overlapping chunks by characters or words.

Chunk sizes and overlaps are measured in characters (``by="chars"``) or in
whitespace-separated words (``by="words"``). Standard library only. Python 3.9+.
"""
from __future__ import annotations

import re
from typing import Any, Dict, Iterator, List, Tuple

__all__ = ["chunk_text", "iter_chunks", "chunk_with_offsets", "__version__"]
__version__ = "1.1.0"

_MODES = ("chars", "words")
_WORD = re.compile(r"\S+")


def _check(text: Any, size: Any, overlap: Any, by: Any) -> None:
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    for label, value in (("size", size), ("overlap", overlap)):
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError(f"{label} must be an integer")
    if size <= 0:
        raise ValueError("size must be > 0")
    if overlap < 0 or overlap >= size:
        raise ValueError("overlap must be >= 0 and < size")
    if by not in _MODES:
        raise ValueError("by must be 'chars' or 'words'")


def _spans(text: str, size: int, overlap: int, by: str) -> Iterator[Tuple[int, int]]:
    """Yield ``(start, end)`` character offsets of every chunk."""
    step = size - overlap
    if by == "chars":
        total = len(text)
        for start in range(0, total, step):
            yield start, min(start + size, total)
            if start + size >= total:
                break
        return
    words = [(m.start(), m.end()) for m in _WORD.finditer(text)]
    total = len(words)
    for start in range(0, total, step):
        group = words[start:start + size]
        yield group[0][0], group[-1][1]
        if start + size >= total:
            break


def iter_chunks(text: str, size: int = 500, overlap: int = 50, by: str = "chars") -> Iterator[str]:
    """Lazily yield chunks; see :func:`chunk_text`."""
    _check(text, size, overlap, by)
    if by == "chars":
        for start, end in _spans(text, size, overlap, by):
            yield text[start:end]
        return
    words = text.split()
    step = size - overlap
    for start in range(0, len(words), step):
        yield " ".join(words[start:start + size])
        if start + size >= len(words):
            break


def chunk_text(text: str, size: int = 500, overlap: int = 50, by: str = "chars") -> List[str]:
    """Return overlapping chunks of ``text``.

    Args:
        text: Input text. An empty (or, for words, whitespace-only) text gives ``[]``.
        size: Chunk length in characters or words. Must be > 0.
        overlap: Units shared by consecutive chunks. Must satisfy ``0 <= overlap < size``.
        by: ``"chars"`` or ``"words"``. Word chunks are joined with single spaces.

    Raises:
        TypeError: ``text`` is not a string, or ``size``/``overlap`` are not integers.
        ValueError: ``size``, ``overlap`` or ``by`` is out of range.
    """
    return list(iter_chunks(text, size, overlap, by))


def chunk_with_offsets(
    text: str, size: int = 500, overlap: int = 50, by: str = "chars"
) -> List[Dict[str, Any]]:
    """Return chunks as ``{"index", "start", "end", "text"}`` dicts.

    ``start`` and ``end`` are character offsets into ``text`` and
    ``text[start:end] == chunk["text"]``. In word mode the chunk text is the exact
    slice of the source, so original whitespace between words is preserved.
    """
    _check(text, size, overlap, by)
    return [
        {"index": i, "start": s, "end": e, "text": text[s:e]}
        for i, (s, e) in enumerate(_spans(text, size, overlap, by))
    ]
