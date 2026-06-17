from __future__ import annotations

from dataclasses import dataclass, field

import lancedb
import pyarrow as pa

from backend.config import settings
from backend.rag.embedder import embedder
from backend.rag.retriever import TABLE_NAME

VECTOR_DIM = 768  # PubMedBERT / neuml/pubmedbert-base-embeddings output dim

# ── Schema ─────────────────────────────────────────────────────────────────
# Common fields (all sources): id, source, source_id, title, text, url,
#                              authors, year, chunk_index, vector
# PubMed-specific:             pmid, doi, journal, mesh_terms
# AWMF-specific:               page (PDF page number)
# Fields absent for a given source are stored as empty string / empty list / 0.

SCHEMA = pa.schema(
    [
        # ── identity ──────────────────────────────────────────────────────────
        pa.field("id", pa.string()),
        pa.field("source", pa.string()),  # awmf | pubmed | clinicaltrials | …
        pa.field("source_id", pa.string()),  # register number, PMID, NCT ID, …
        # ── content ───────────────────────────────────────────────────────────
        pa.field("title", pa.string()),
        pa.field("text", pa.string()),  # indexed chunk
        # ── common metadata ───────────────────────────────────────────────────
        pa.field("url", pa.string()),
        pa.field("authors", pa.list_(pa.string())),
        pa.field("year", pa.int32()),
        pa.field("chunk_index", pa.int32()),
        # ── PubMed-specific ───────────────────────────────────────────────────
        pa.field("pmid", pa.string()),
        pa.field("doi", pa.string()),
        pa.field("journal", pa.string()),
        pa.field("mesh_terms", pa.list_(pa.string())),
        # ── AWMF-specific ─────────────────────────────────────────────────────
        pa.field("page", pa.int32()),  # PDF page number
        # ── vector ────────────────────────────────────────────────────────────
        pa.field("vector", pa.list_(pa.float32(), VECTOR_DIM)),
    ]
)


@dataclass
class Document:
    # required
    id: str
    source: str  # "awmf", "pubmed", etc.
    title: str
    text: str  # the indexed chunk

    # common optional
    source_id: str = ""  # register number, PMID, NCT number, …
    url: str = ""
    authors: list[str] = field(default_factory=list)
    year: int = 0
    chunk_index: int = 0

    # PubMed-specific
    pmid: str = ""
    doi: str = ""
    journal: str = ""
    mesh_terms: list[str] = field(default_factory=list)

    # AWMF-specific
    page: int = 0  # PDF page number; 0 = N/A


def ingest(documents: list[Document], drop_existing: bool = False) -> int:
    db = lancedb.connect(settings.lancedb_path)

    if drop_existing:
        try:
            db.drop_table(TABLE_NAME)
        except Exception:
            pass

    try:
        tbl = db.open_table(TABLE_NAME)
    except Exception:
        tbl = db.create_table(TABLE_NAME, schema=SCHEMA)

    rows = []
    for doc in documents:
        vector = embedder.embed_article(doc.title + " " + doc.text)
        rows.append(
            {
                "id": doc.id,
                "source": doc.source,
                "source_id": doc.source_id,
                "title": doc.title,
                "text": doc.text,
                "url": doc.url,
                "authors": doc.authors,
                "year": doc.year,
                "chunk_index": doc.chunk_index,
                "pmid": doc.pmid,
                "doi": doc.doi,
                "journal": doc.journal,
                "mesh_terms": doc.mesh_terms,
                "page": doc.page,
                "vector": vector,
            }
        )

    tbl.add(rows)
    return len(rows)
