
# File 2 — `src/retrieval_pipeline.py`

```python
"""Composable retrieval-to-context workflow for AI applications."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any


Retriever = Callable[..., Any]
ContextBuilder = Callable[..., str]


def build_retrieval_context(
    query: str,
    documents: Sequence[str],
    *,
    retrieve: Retriever,
    build_context: ContextBuilder,
    top_k: int = 5,
    max_chars: int = 4000,
) -> str:
    """Retrieve passages and transform them into bounded AI-ready context.

    Args:
        query: User retrieval query.
        documents: Candidate text documents or passages.
        retrieve: Adapter connected to the selected retrieval component.
        build_context: Adapter connected to the selected context builder.
        top_k: Maximum number of passages to retrieve.
        max_chars: Maximum number of characters in the final context.

    Returns:
        A non-empty context string produced by ``build_context``.

    Raises:
        TypeError: If an argument has an invalid type.
        ValueError: If query, documents, top_k, max_chars, or retrieval output
            is invalid.
        TypeError: If retrieve or build_context is not callable.
    """
    if not isinstance(query, str):
        raise TypeError("query must be a string")

    if not query.strip():
        raise ValueError("query cannot be empty")

    if not isinstance(documents, Sequence) or isinstance(documents, (str, bytes)):
        raise TypeError("documents must be a sequence of strings")

    if any(not isinstance(document, str) for document in documents):
        raise TypeError("every document must be a string")

    if not callable(retrieve):
        raise TypeError("retrieve must be callable")

    if not callable(build_context):
        raise TypeError("build_context must be callable")

    if not isinstance(top_k, int) or isinstance(top_k, bool):
        raise TypeError("top_k must be an integer")

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero")

    if not isinstance(max_chars, int) or isinstance(max_chars, bool):
        raise TypeError("max_chars must be an integer")

    if max_chars <= 0:
        raise ValueError("max_chars must be greater than zero")

    passages = retrieve(query, documents, top_k=top_k)

    if passages is None:
        raise ValueError("retriever returned no result")

    selected = list(passages)

    if not selected:
        raise ValueError("retriever returned no passages")

    normalized: list[str] = []

    for passage in selected:
        if isinstance(passage, str):
            text = passage
        elif isinstance(passage, (tuple, list)) and passage:
            text = passage[0]
        elif isinstance(passage, dict):
            text = passage.get("text", "")
        else:
            raise TypeError("retriever returned an unsupported passage type")

        if not isinstance(text, str):
            raise TypeError("retrieved passage text must be a string")

        text = text.strip()

        if text:
            normalized.append(text)

    if not normalized:
        raise ValueError("retriever returned no usable text")

    context = build_context(normalized, max_chars=max_chars)

    if not isinstance(context, str):
        raise TypeError("context builder must return a string")

    context = context.strip()

    if not context:
        raise ValueError("context builder returned empty context")

    return context