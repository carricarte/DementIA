import pytest

from backend.rag.ingestion import Document


def test_document_dataclass():
    doc = Document(id="1", source="pubmed", title="Test", text="Body text")
    assert doc.url == ""
    assert doc.pmid == ""


def test_ingest_and_retrieve(tmp_path, monkeypatch):
    """Round-trip: ingest a document, retrieve it by query."""
    import numpy as np

    from backend.rag.embedder import embedder
    from backend.rag.ingestion import ingest
    from backend.rag.retriever import KnowledgeRetriever

    monkeypatch.setattr("backend.config.settings.lancedb_path", str(tmp_path / "lancedb"))
    monkeypatch.setattr(embedder, "embed_query", lambda t: [0.1] * 768)
    monkeypatch.setattr(embedder, "embed_article", lambda t: [0.1] * 768)

    docs = [Document(id="d1", source="pubmed", title="Alzheimer review", text="Key findings")]
    ingest(docs)

    ret = KnowledgeRetriever()
    text, citations = ret.retrieve("alzheimer", top_k=1)
    assert len(citations) == 1
    assert citations[0].source == "pubmed"
