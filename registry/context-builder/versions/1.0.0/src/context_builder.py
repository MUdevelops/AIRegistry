"""context-builder: turn retrieved passages into a structured context block.

format_context() works standalone. build_context() uses the keyword-rag component.
"""
import os
import sys


def _load_retrieve():
    try:
        from keyword_rag import retrieve
    except ImportError:  # installed layout: ai_components/<name>/src/
        here = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, os.path.join(here, "..", "..", "keyword-rag", "src"))
        from keyword_rag import retrieve
    return retrieve


def format_context(results, max_chars=2000, header="Context"):
    """results: list of {'id','text', optional 'score'}. Returns a numbered block within max_chars."""
    lines, used = [], 0
    for i, r in enumerate(results, 1):
        text = " ".join(r["text"].split())
        entry = f"[{i}] ({r.get('id', i)}) {text}"
        if used + len(entry) > max_chars:
            room = max_chars - used - 4
            if room > 20:
                lines.append(entry[:room].rstrip() + "...")
            break
        lines.append(entry)
        used += len(entry) + 1
    return f"<{header.lower()}>\n" + "\n".join(lines) + f"\n</{header.lower()}>" if lines else ""


def build_context(query, documents, top_k=3, max_chars=2000):
    """Retrieve the best documents for query and format them as a context block."""
    return format_context(_load_retrieve()(documents, query, top_k), max_chars)
