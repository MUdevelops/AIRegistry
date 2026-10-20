"""retrieval-pipeline: compose retrieval and context building into one workflow.

The pipeline is adapter based: you pass a ``retrieve`` callable and a
``build_context`` callable, so it works with any retriever and any context
formatter (for example the ``keyword-rag`` and ``context-builder`` components)
without importing them. Standard library only. Python 3.9+.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

__all__ = ["RetrievalPipeline", "RetrievalResult", "build_retrieval_context", "__version__"]
__version__ = "1.1.0"

Retriever = Callable[..., Any]
ContextBuilder = Callable[..., str]


@dataclass(frozen=True)
class RetrievalResult:
    """Outcome of one pipeline run."""

    query: str
    retrieval_query: str
    passages: Tuple[str, ...]
    context: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "retrieval_query": self.retrieval_query,
            "passages": list(self.passages),
            "context": self.context,
        }


def _positive_int(name: str, value: Any) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be an integer")
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero")
    return value


def _passage_text(passage: Any) -> str:
    if isinstance(passage, str):
        text = passage
    elif isinstance(passage, (tuple, list)) and passage:
        text = passage[0]
    elif isinstance(passage, Mapping):
        text = passage.get("text", "")
    else:
        raise TypeError("retriever returned an unsupported passage type")
    if not isinstance(text, str):
        raise TypeError("retrieved passage text must be a string")
    return text.strip()


class RetrievalPipeline:
    """Query -> (optional rewrite) -> retrieve -> normalize passages -> build context.

    Args:
        retrieve: ``retrieve(query, documents, top_k=top_k)`` returning passages. Passages may be
            strings, mappings with ``text``, or sequences whose first item is the text.
        build_context: ``build_context(passages, max_chars=max_chars)`` receiving a list of
            passage strings and returning the context string.
        top_k: Maximum passages to retrieve (> 0).
        max_chars: Character budget passed to ``build_context`` (> 0).
        rewrite_query: Optional ``str -> str`` applied to the query before retrieval.
        on_empty: ``"raise"`` (default) raises ``ValueError`` when nothing usable is retrieved;
            ``"empty"`` returns a result with an empty context instead.
    """

    def __init__(
        self,
        retrieve: Retriever,
        build_context: ContextBuilder,
        *,
        top_k: int = 5,
        max_chars: int = 4000,
        rewrite_query: Optional[Callable[[str], str]] = None,
        on_empty: str = "raise",
    ) -> None:
        if not callable(retrieve):
            raise TypeError("retrieve must be callable")
        if not callable(build_context):
            raise TypeError("build_context must be callable")
        if rewrite_query is not None and not callable(rewrite_query):
            raise TypeError("rewrite_query must be callable")
        if on_empty not in ("raise", "empty"):
            raise ValueError("on_empty must be 'raise' or 'empty'")
        self.retrieve = retrieve
        self.build_context = build_context
        self.top_k = _positive_int("top_k", top_k)
        self.max_chars = _positive_int("max_chars", max_chars)
        self.rewrite_query = rewrite_query
        self.on_empty = on_empty

    def run(self, query: str, documents: Sequence[str]) -> RetrievalResult:
        """Run the pipeline over ``documents`` (a sequence of strings)."""
        if not isinstance(query, str):
            raise TypeError("query must be a string")
        if not query.strip():
            raise ValueError("query cannot be empty")
        if not isinstance(documents, Sequence) or isinstance(documents, (str, bytes)):
            raise TypeError("documents must be a sequence of strings")
        if any(not isinstance(document, str) for document in documents):
            raise TypeError("every document must be a string")

        retrieval_query = query
        if self.rewrite_query is not None:
            retrieval_query = self.rewrite_query(query)
            if not isinstance(retrieval_query, str) or not retrieval_query.strip():
                raise ValueError("rewrite_query must return a non-empty string")

        found = self.retrieve(retrieval_query, documents, top_k=self.top_k)
        if found is None:
            raise ValueError("retriever returned no result")
        passages: List[str] = [t for t in (_passage_text(p) for p in list(found)) if t]

        if not passages:
            if self.on_empty == "empty":
                return RetrievalResult(query, retrieval_query, (), "")
            raise ValueError("retriever returned no usable passages")

        context = self.build_context(passages, max_chars=self.max_chars)
        if not isinstance(context, str):
            raise TypeError("context builder must return a string")
        context = context.strip()
        if not context:
            if self.on_empty == "empty":
                return RetrievalResult(query, retrieval_query, tuple(passages), "")
            raise ValueError("context builder returned empty context")
        return RetrievalResult(query, retrieval_query, tuple(passages), context)

    __call__ = run


def build_retrieval_context(
    query: str,
    documents: Sequence[str],
    *,
    retrieve: Retriever,
    build_context: ContextBuilder,
    top_k: int = 5,
    max_chars: int = 4000,
) -> str:
    """One-call form: returns only the context string. See :class:`RetrievalPipeline`."""
    pipeline = RetrievalPipeline(retrieve, build_context, top_k=top_k, max_chars=max_chars)
    return pipeline.run(query, documents).context
