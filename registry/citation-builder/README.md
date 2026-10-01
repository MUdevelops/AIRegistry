# citation-builder

Format numbered source citations and bibliographies from source metadata.

## Install

```bash
ai add citation-builder
```

Python standard library only.

## API

`format_citation(index, source)`, `build_citations(sources, start=1)` (merges duplicates), `bibliography(sources)` and `markers([1, 3])`. A source is a dict with `title` and optional `author`, `date`, `url`.

## Example

```python
from citation_builder import bibliography

print(bibliography([{"title": "Attention Is All You Need", "author": "Vaswani et al.", "date": "2017"}]))
```
