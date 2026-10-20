# citation-builder

**Version 1.1.0** · Python 3.9+ · standard library only · MIT

Format numbered source citations and bibliographies from source metadata, with duplicate merging and stable numbering for RAG answers.

## Install

```bash
ai add citation-builder@1.1.0
```

## Quick start

```python
from citation_builder import CitationIndex, build_citations, bibliography, markers

sources = [
    {"title": "Notes on the Analytical Engine", "author": "Ada Lovelace", "date": "1843", "url": "https://example.org/notes"},
    {"title": "Python Docs", "url": "https://docs.python.org/3/"},
]

build_citations(sources)
# ['[1] Ada Lovelace. Notes on the Analytical Engine (1843). https://example.org/notes',
#  '[2] Python Docs. https://docs.python.org/3/']

print(bibliography(sources))        # "Sources\n[1] ...\n[2] ..."
markers([2, 1, 2])                  # '[1][2]'

# Stable numbers while an answer is being written:
index = CitationIndex()
n = index.add(sources[0])           # 1 (adding the same URL again returns 1)
```

## API

| Name | Description |
|---|---|
| `format_citation(index, source)` | One line: `[n] Author. Title (date). url`. |
| `build_citations(sources, start=1)` | Numbered lines, duplicates merged. |
| `bibliography(sources, heading="Sources", start=1)` | Heading plus citations; `""` if there are no sources. |
| `markers(numbers)` | Sorted, de-duplicated inline markers such as `[1][3]`. |
| `CitationIndex(start=1)` | `.add(source) -> int`, `.citations()`, `.bibliography()`, `len(index)`. |

A source is a mapping with a required `title` and optional `author`, `date` and `url`.

## Behavior

- Sources are the same when their URL matches (case-insensitive, ignoring a trailing slash and `#fragment`); sources without a URL match on title.
- Whitespace in fields is collapsed. A title ending in `.`, `?` or `!` does not get an extra full stop.
- A source without a title raises `ValueError`; a non-mapping source raises `TypeError`.

## Changes in 1.1.0

Adds `CitationIndex`, URL-aware de-duplication, whitespace cleanup, punctuation handling, and input validation. `bibliography()` now returns `""` for an empty list instead of a bare heading.
