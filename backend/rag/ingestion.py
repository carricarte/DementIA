from __future__ import annotations

from dataclasses import dataclass, field

import lancedb
import pyarrow as pa

from backend.config import settings
from backend.rag.embedder import embedder
from backend.rag.retriever import TABLE_NAME

VECTOR_DIM = 768  # MedCPT article encoder output

SCHEMA = pa.schema([
    pa.field("id", pa.string()),
    pa.field("source", pa.string()),        # awmf | pubmed | clinicaltrials | neurology | alz | aan
    pa.field("source_id", pa.string()),     # register number, PMID, NCT ID, etc.
    pa.field("title", pa.string()),
    pa.field("text", pa.string()),
    pa.field("url", pa.string()),
    pa.field("pmid", pa.string()),
    pa.field("authors", pa.list_(pa.string())),
    pa.field("year", pa.int32()),
    pa.field("page", pa.int32()),
    pa.field("chunk_index", pa.int32()),
    pa.field("vector", pa.list_(pa.float32(), VECTOR_DIM)),
])


@dataclass
class Document:
    id: str
    source: str             # "awmf", "pubmed", etc.
    title: str
    text: str
    source_id: str = ""     # e.g. "038-013", PMID, NCT number
    url: str = ""
    pmid: str = ""
    authors: list[str] = field(default_factory=list)
    year: int = 0           # 0 = unknown
    page: int = 0           # 0 = N/A
    chunk_index: int = 0


def ingest(documents: list[Document]) -> int:
    db = lancedb.connect(settings.lancedb_path)

    try:
        tbl = db.open_table(TABLE_NAME)
    except Exception:
        tbl = db.create_table(TABLE_NAME, schema=SCHEMA)

    rows = []
    for doc in documents:
        vector = embedder.embed_article(doc.title + " " + doc.text)
        rows.append({
            "id": doc.id,
            "source": doc.source,
            "source_id": doc.source_id,
            "title": doc.title,
            "text": doc.text,
            "url": doc.url,
            "pmid": doc.pmid,
            "authors": doc.authors,
            "year": doc.year,
            "page": doc.page,
            "chunk_index": doc.chunk_index,
            "vector": vector,
        })

    tbl.add(rows)
    return len(rows)
