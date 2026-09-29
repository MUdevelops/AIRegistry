"""Numbered citation formatting. Source = {"title": str, "url": str}."""


def cite(sources):
    return [f"[{i}] {s['title']} ({s['url']})" for i, s in enumerate(sources, 1)]


def annotate(text, sources):
    return text + "\n\n" + "\n".join(cite(sources))
