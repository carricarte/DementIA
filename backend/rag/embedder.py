from __future__ import annotations

from backend.config import settings


class SentenceEmbedder:
    """Wraps a sentence-transformers model for symmetric query+article embedding.

    MedCPT (ncats/MedCPT-*) requires HuggingFace org-level authentication so
    we use neuml/pubmedbert-base-embeddings by default — same 768-dim output,
    built on PubMedBERT, designed for biomedical document retrieval.
    """

    def __init__(self) -> None:
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(settings.embed_model)

    def embed_query(self, text: str) -> list[float]:
        return self._model.encode(text, normalize_embeddings=True).tolist()

    def embed_article(self, text: str) -> list[float]:
        return self._model.encode(text, normalize_embeddings=True).tolist()


class _LazyEmbedder:
    """Defers model download until the first embed call."""

    _inner: SentenceEmbedder | None = None

    def _get(self) -> SentenceEmbedder:
        if self._inner is None:
            self._inner = SentenceEmbedder()
        return self._inner

    def embed_query(self, text: str) -> list[float]:
        return self._get().embed_query(text)

    def embed_article(self, text: str) -> list[float]:
        return self._get().embed_article(text)


embedder = _LazyEmbedder()
