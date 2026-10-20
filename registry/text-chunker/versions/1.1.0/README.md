# text-chunker

**Version 1.1.0** · Python 3.9+ · standard library only · MIT

Split text into overlapping chunks by characters or words, the usual first step before embedding or retrieval.

## Install

```bash
ai add text-chunker@1.1.0
```

## Quick start

```python
from text_chunker import chunk_text, chunk_with_offsets

chunk_text("abcdefghij", size=4, overlap=1)
# ['abcd', 'defg', 'ghij']

chunk_text("one two three four five", size=3, overlap=1, by="words")
# ['one two three', 'three four five']

chunk_with_offsets("abcdef", size=4, overlap=2)[1]
# {'index': 1, 'start': 2, 'end': 6, 'text': 'cdef'}
```

## API

| Function | Description |
|---|---|
| `chunk_text(text, size=500, overlap=50, by="chars")` | Returns a list of chunks. |
| `iter_chunks(text, size=500, overlap=50, by="chars")` | Same chunks as a lazy iterator. |
| `chunk_with_offsets(text, size=500, overlap=50, by="chars")` | Chunks as `{index, start, end, text}` with character offsets into the source. |

`by` is `"chars"` or `"words"` (whitespace-separated). Both `size` and `overlap` are in that unit.

## Behavior

- Every chunk starts `size - overlap` units after the previous one, and the final chunk always reaches the end of the text.
- Empty input returns `[]`. No empty chunks are produced.
- `chunk_text` joins word chunks with single spaces; `chunk_with_offsets` returns the exact source slice, so `text[start:end] == chunk["text"]` always holds.
- Invalid arguments raise `TypeError` (wrong types) or `ValueError` (`size <= 0`, `overlap` outside `0 <= overlap < size`, unknown `by`).

## Changes in 1.1.0

`iter_chunks`, word-mode support in `chunk_with_offsets`, strict type checks, and exact offsets for all modes. Chunking output is unchanged from 1.0.0.
