# text-chunker

Split text into configurable chunks with overlap, by characters or words.

## Install

```bash
ai add text-chunker
```

Python standard library only.

## API

`chunk_text(text, size=500, overlap=50, by="chars")` returns a list of chunks (`by="words"` counts words). `chunk_with_offsets(text, size, overlap)` returns dicts with `index`, `start`, `end`, `text`. Raises `ValueError` if `overlap >= size`.

## Example

```python
from text_chunker import chunk_text

print(chunk_text("one two three four five six", size=3, overlap=1, by="words"))
# ['one two three', 'three four five', 'five six']
```
