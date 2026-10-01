"""text-chunker: split text into overlapping chunks by characters or words."""


def chunk_text(text, size=500, overlap=50, by="chars"):
    """Return a list of chunks. size/overlap are in characters or words (by='words')."""
    if size <= 0:
        raise ValueError("size must be > 0")
    if overlap < 0 or overlap >= size:
        raise ValueError("overlap must be >= 0 and < size")
    if by not in ("chars", "words"):
        raise ValueError("by must be 'chars' or 'words'")
    units = text.split() if by == "words" else text
    joiner = " " if by == "words" else ""
    step = size - overlap
    chunks = []
    for start in range(0, len(units), step):
        piece = units[start:start + size]
        if piece:
            chunks.append(joiner.join(piece) if by == "words" else piece)
        if start + size >= len(units):
            break
    return chunks


def chunk_with_offsets(text, size=500, overlap=50):
    """Character chunks as dicts: {index, start, end, text}."""
    chunks = chunk_text(text, size, overlap, "chars")
    step = size - overlap
    return [{"index": i, "start": i * step, "end": i * step + len(c), "text": c}
            for i, c in enumerate(chunks)]
