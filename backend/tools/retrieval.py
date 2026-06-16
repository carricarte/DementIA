from __future__ import annotations

from typing import TypedDict

from backend.state.schema import Citation


class RetrievalResult(TypedDict):
    text: str
    citations: list[Citation]


def retrieve(
    query: str,
    source_filter: list[str] | None = None,
    top_k: int | None = None,
) -> RetrievalResult:
    from backend.rag.retriever import retriever  # late import avoids model load at startup
    text, citations = retriever.retrieve(query, source_filter=source_filter, top_k=top_k)
    return {"text": text, "citations": citations}
