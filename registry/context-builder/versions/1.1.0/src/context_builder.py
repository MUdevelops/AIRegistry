"""context-builder: turn retrieved passages into a size-limited prompt context block.

``format_context`` is self-contained. ``build_context`` retrieves first and then
formats; it accepts any retriever and falls back to the ``keyword-rag``
component when that is installed. Standard library only. Python 3.9+.
"""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from typing import Any, Callable, Iterable, List, Mapping, Optional, Union

__all__ = ["format_context", "build_context", "__version__"]
__version__ = "1.1.0"

Passage = Union[str, Mapping[str, Any]]
Retriever = Callable[[Iterable[Any], str, int], Iterable[Passage]]

_HEADER = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
_MIN_TRUNCATED = 24


def _positive(name: str, value: Any) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be an integer")
    if value < 1:
        raise ValueError(f"{name} must be >= 1")
    return value


def _entry(number: int, passage: Passage) -> str:
    if isinstance(passage, str):
        text, label = passage, ""
    elif isinstance(passage, Mapping) and isinstance(passage.get("text"), str):
        text, label = passage["text"], f"({passage.get('id', number)}) "
    else:
        raise TypeError("each passage must be a string or a mapping with a string 'text'")
    return f"[{number}] {label}{' '.join(text.split())}"


def format_context(
    results: Iterable[Passage], max_chars: int = 2000, header: str = "context"
) -> str:
    """Format passages as a numbered block wrapped in ``<header>`` tags.

    Args:
        results: Strings, or mappings with ``text`` and optional ``id`` (as returned by
            ``keyword-rag``). Whitespace inside a passage is collapsed.
        max_chars: Budget for the numbered lines, including the newlines between them
            (the wrapper tags are not counted). The first passage that does not fit is
            shortened with ``...`` when at least 24 characters remain; later passages are dropped.
        header: Tag name, for example ``context`` or ``sources``.

    Returns:
        The block, or ``""`` when nothing fits or there are no passages.
    """
    _positive("max_chars", max_chars)
    if not isinstance(header, str) or not _HEADER.match(header):
        raise ValueError("header must start with a letter and contain only letters, digits, '_' or '-'")
    if isinstance(results, (str, bytes)):
        raise TypeError("results must be a list of passages, not a single string")
    lines: List[str] = []
    used = 0
    for number, passage in enumerate(results, 1):
        entry = _entry(number, passage)
        cost = len(entry) + (1 if lines else 0)
        if used + cost <= max_chars:
            lines.append(entry)
            used += cost
            continue
        room = max_chars - used - (1 if lines else 0)
        if room >= _MIN_TRUNCATED:
            lines.append(entry[: room - 3].rstrip() + "...")
        break
    if not lines:
        return ""
    tag = header.lower()
    return f"<{tag}>\n" + "\n".join(lines) + f"\n</{tag}>"


def _default_retriever() -> Retriever:
    """Find ``keyword_rag.retrieve``: importable, or the sibling AIRegistry install."""
    try:
        from keyword_rag import retrieve  # type: ignore[import-not-found]
        return retrieve
    except ImportError:
        pass
    here = Path(__file__).resolve().parent  # .../ai_components/context-builder/src
    for candidate in (here.parent.parent / "keyword-rag" / "src" / "keyword_rag.py", here / "keyword_rag.py"):
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("keyword_rag", candidate)
            module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
            spec.loader.exec_module(module)  # type: ignore[union-attr]
            return module.retrieve
    raise ImportError(
        "build_context needs a retriever: pass retrieve=... or install keyword-rag (ai add keyword-rag)"
    )


def build_context(
    query: str,
    documents: Iterable[Any],
    top_k: int = 3,
    max_chars: int = 2000,
    *,
    retrieve: Optional[Retriever] = None,
    header: str = "context",
) -> str:
    """Retrieve the best documents for ``query`` and format them as a context block.

    ``retrieve`` is called as ``retrieve(documents, query, top_k)`` and must return passages
    in the shapes accepted by :func:`format_context`. When omitted, ``keyword_rag.retrieve`` is used.
    """
    if not isinstance(query, str):
        raise TypeError("query must be a string")
    _positive("top_k", top_k)
    search = retrieve if retrieve is not None else _default_retriever()
    return format_context(search(documents, query, top_k), max_chars, header)
