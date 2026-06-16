from __future__ import annotations

import lancedb

from backend.config import settings
from backend.rag.embedder import embedder
from backend.state.schema import Citation

TABLE_NAME = "knowledge"


class KnowledgeRetriever:
    def __init__(self) -> None:
        self._db = lancedb.connect(settings.lancedb_path)

    def retrieve(
        self,
        query: str,
        source_filter: list[str] | None = None,
        top_k: int | None = None,
    ) -> tuple[str, list[Citation]]:
        k = top_k or settings.retrieval_top_k

        try:
            tbl = self._db.open_table(TABLE_NAME)
        except Exception:
            return "", []  # knowledge base not yet populated

        vector = embedder.embed_query(query)

        results = tbl.search(vector).limit(k * 2).to_pandas()

        if source_filter:
            results = results[results["source"].isin(source_filter)]
        results = results.head(k)

        chunks = results["text"].tolist()

        # Deduplicate citations: keep one entry per unique (source, title) pair,
        # preserving the retrieval order so the most relevant document appears first.
        seen: set[tuple[str, str]] = set()
        citations: list[Citation] = []
        for _, row in results.iterrows():
            key = (row["source"], row["title"])
            if key in seen:
                continue
            seen.add(key)
            citations.append(Citation(
                source=row["source"],
                title=row["title"],
                url=row.get("url") or None,
                pmid=row.get("pmid") or None,
            ))

        return "\n\n---\n\n".join(chunks), citations


retriever = KnowledgeRetriever()
