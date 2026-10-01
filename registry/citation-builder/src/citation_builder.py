"""citation-builder: format numbered source citations."""


def format_citation(index, source):
    """Format one source dict (title, url, author, date) as '[n] Author. Title (date). url'."""
    title = (source.get("title") or "").strip()
    if not title:
        raise ValueError("source needs a title")
    text = f"[{index}] "
    if source.get("author"):
        text += f"{source['author'].strip()}. "
    text += title
    if source.get("date"):
        text += f" ({source['date']})"
    text += "."
    if source.get("url"):
        text += f" {source['url'].strip()}"
    return text


def build_citations(sources, start=1):
    """Return a list of numbered citation strings. Duplicate sources (same url/title) are merged."""
    seen, out = set(), []
    for s in sources:
        key = (s.get("url") or s.get("title") or "").strip().lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(format_citation(start + len(out), s))
    return out


def bibliography(sources, heading="Sources"):
    return heading + "\n" + "\n".join(build_citations(sources))


def markers(numbers):
    """markers([1, 3]) -> '[1][3]'"""
    return "".join(f"[{n}]" for n in sorted(set(numbers)))
