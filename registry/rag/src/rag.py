"""Tiny keyword retriever: rank documents by shared terms."""
import re


def terms(s):
    return set(re.findall(r"\w+", s.lower()))


def retrieve(query, docs, k=3):
    q = terms(query)
    scored = sorted(((len(q & terms(d)), i) for i, d in enumerate(docs)), key=lambda x: (-x[0], x[1]))
    return [docs[i] for s, i in scored[:k] if s]


def answer(query, docs):
    return {"query": query, "context": retrieve(query, docs)}
