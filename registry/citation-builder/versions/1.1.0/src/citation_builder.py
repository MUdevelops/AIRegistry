"""citation-builder: numbered source citations and bibliographies.

Turns source metadata (``title``, ``url``, ``author``, ``date``) into numbered
citation lines such as ``[1] Ada Lovelace. Notes (1843). https://example.org``,
merging duplicate sources. Standard library only. Python 3.9+.
"""
from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Mapping, Optional

__all__ = [
    "CitationIndex", "format_citation", "build_citations", "bibliography", "markers", "__version__",
]
__version__ = "1.1.0"

_SPACES = re.compile(r"\s+")


def _text(source: Mapping[str, Any], key: str) -> str:
    value = source.get(key)
    return _SPACES.sub(" ", str(value)).strip() if value not in (None, "") else ""


def _check_source(source: Any) -> Mapping[str, Any]:
    if not isinstance(source, Mapping):
        raise TypeError("source must be a mapping with at least a 'title'")
    if not _text(source, "title"):
        raise ValueError("source needs a title")
    return source


def _key(source: Mapping[str, Any]) -> str:
    """Identity used to merge duplicates: normalized URL when present, otherwise the title."""
    url = _text(source, "url").lower().split("#", 1)[0].rstrip("/")
    return url or _text(source, "title").lower()


def format_citation(index: int, source: Mapping[str, Any]) -> str:
    """Format one source as ``[n] Author. Title (date). url``.

    Missing optional fields are omitted. A title that already ends in ``.``, ``?``
    or ``!`` does not get a second full stop.
    """
    if not isinstance(index, int) or isinstance(index, bool) or index < 1:
        raise ValueError("index must be a positive integer")
    source = _check_source(source)
    line = f"[{index}] "
    if _text(source, "author"):
        line += _text(source, "author").rstrip(".") + ". "
    line += _text(source, "title")
    if _text(source, "date"):
        line += f" ({_text(source, 'date')})"
    if not line.endswith((".", "?", "!")):
        line += "."
    if _text(source, "url"):
        line += " " + _text(source, "url")
    return line


class CitationIndex:
    """Assign stable citation numbers to sources across a whole answer.

    >>> index = CitationIndex()
    >>> index.add({"title": "A", "url": "https://a.example"})
    1
    >>> index.add({"title": "A again", "url": "https://a.example/"})
    1
    """

    def __init__(self, start: int = 1) -> None:
        if not isinstance(start, int) or isinstance(start, bool) or start < 1:
            raise ValueError("start must be a positive integer")
        self._start = start
        self._numbers: Dict[str, int] = {}
        self._sources: List[Mapping[str, Any]] = []

    def add(self, source: Mapping[str, Any]) -> int:
        """Register a source and return its number. Duplicates return the existing number."""
        source = _check_source(source)
        key = _key(source)
        if key not in self._numbers:
            self._numbers[key] = self._start + len(self._sources)
            self._sources.append(source)
        return self._numbers[key]

    def citations(self) -> List[str]:
        """All registered citations, in numbering order."""
        return [format_citation(self._start + i, s) for i, s in enumerate(self._sources)]

    def bibliography(self, heading: str = "Sources") -> str:
        """Heading plus all citations, or an empty string when nothing is registered."""
        return _join(heading, self.citations())

    def __len__(self) -> int:
        return len(self._sources)


def build_citations(sources: Iterable[Mapping[str, Any]], start: int = 1) -> List[str]:
    """Return numbered citation lines for ``sources``; duplicates are merged."""
    index = CitationIndex(start)
    for source in sources:
        index.add(source)
    return index.citations()


def _join(heading: str, citations: List[str]) -> str:
    if not citations:
        return ""
    return (heading.strip() + "\n" if heading.strip() else "") + "\n".join(citations)


def bibliography(
    sources: Iterable[Mapping[str, Any]], heading: Optional[str] = "Sources", start: int = 1
) -> str:
    """Return ``heading`` followed by the citations, or ``""`` when there are no sources."""
    return _join(heading or "", build_citations(sources, start))


def markers(numbers: Iterable[int]) -> str:
    """Render inline markers: ``markers([3, 1, 3]) -> '[1][3]'``."""
    cleaned = set()
    for n in numbers:
        if not isinstance(n, int) or isinstance(n, bool) or n < 1:
            raise ValueError("citation numbers must be positive integers")
        cleaned.add(n)
    return "".join(f"[{n}]" for n in sorted(cleaned))
