"""keyword-rag: lightweight keyword retrieval over documents (no dependencies)."""
import math
import re

STOPWORDS = frozenset("a an and are as at be by for from has in is it of on or that the to was were with".split())


def tokenize(text):
    return [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS]


def retrieve(documents, query, top_k=3):
    """documents: list of strings or {'id', 'text'} dicts.

    Returns up to top_k dicts {id, score, text} ranked by TF-IDF-style keyword score.
    """
    docs = []
    for i, d in enumerate(documents):
        if isinstance(d, str):
            d = {"id": i, "text": d}
        docs.append({"id": d.get("id", i), "text": d["text"], "tokens": tokenize(d["text"])})
    q = set(tokenize(query))
    if not docs or not q:
        return []
    n = len(docs)
    results = []
    for d in docs:
        score = 0.0
        for term in q:
            tf = d["tokens"].count(term)
            if tf:
                df = sum(1 for x in docs if term in x["tokens"])
                score += (1 + math.log(tf)) * (math.log((n + 1) / df) + 1)
        if score > 0:
            results.append({"id": d["id"], "score": round(score, 4), "text": d["text"]})
    results.sort(key=lambda r: (-r["score"], str(r["id"])))
    return results[:top_k]


class KeywordRetriever:
    def __init__(self):
        self.documents = []

    def add_document(self, text, id=None):
        self.documents.append({"id": len(self.documents) if id is None else id, "text": text})

    def retrieve(self, query, top_k=3):
        return retrieve(self.documents, query, top_k)
