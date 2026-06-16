"""
Ingest documents into the DCA knowledge base (LanceDB).

Usage:
    python scripts/ingest.py --source awmf
    python scripts/ingest.py --source pubmed --query "dementia treatment"
    python scripts/ingest.py --all

Requires the [ingest,rag] optional dependencies:
    pip install -e ".[ingest,rag]"
"""
from __future__ import annotations

import argparse
import sys

sys.path.insert(0, ".")

from backend.rag.ingestion import Document, ingest

SOURCES = ["pubmed", "clinicaltrials", "neurology", "alz", "aan", "awmf"]


def fetch_awmf() -> list[Document]:
    from backend.rag.sources.awmf import fetch
    return fetch()


def fetch_pubmed(query: str, max_results: int = 200) -> list[Document]:
    raise NotImplementedError("PubMed fetcher not yet implemented")


def fetch_clinicaltrials(query: str, max_results: int = 100) -> list[Document]:
    raise NotImplementedError("ClinicalTrials fetcher not yet implemented")


def fetch_neurology(query: str) -> list[Document]:
    raise NotImplementedError("Neurology.org fetcher not yet implemented")


def fetch_alz(query: str) -> list[Document]:
    raise NotImplementedError("Alz.org fetcher not yet implemented")


def fetch_aan(query: str) -> list[Document]:
    raise NotImplementedError("AAN.com fetcher not yet implemented")


def main() -> None:
    parser = argparse.ArgumentParser(description="Populate the DCA LanceDB knowledge base")
    parser.add_argument("--source", choices=SOURCES, help="Single source to ingest")
    parser.add_argument("--all", action="store_true", help="Ingest all sources")
    parser.add_argument("--query", default="dementia", help="Search query for API-based sources")
    args = parser.parse_args()

    if not args.all and not args.source:
        parser.print_help()
        return

    sources = SOURCES if args.all else [args.source]
    total = 0

    for src in sources:
        print(f"\n[{src}] Fetching ...")
        try:
            if src == "awmf":
                docs = fetch_awmf()
            elif src == "pubmed":
                docs = fetch_pubmed(args.query)
            elif src == "clinicaltrials":
                docs = fetch_clinicaltrials(args.query)
            elif src == "neurology":
                docs = fetch_neurology(args.query)
            elif src == "alz":
                docs = fetch_alz(args.query)
            elif src == "aan":
                docs = fetch_aan(args.query)
            else:
                print(f"  {src}: no fetcher, skipping")
                continue

            if not docs:
                print(f"  {src}: 0 documents returned")
                continue

            print(f"  Embedding and storing {len(docs)} chunks ...")
            n = ingest(docs)
            print(f"  {src}: ingested {n} chunks")
            total += n

        except NotImplementedError as e:
            print(f"  {src}: {e}")
        except Exception as e:
            print(f"  {src}: unexpected error — {e}")
            raise

    print(f"\nDone. Total chunks ingested: {total}")


if __name__ == "__main__":
    main()
