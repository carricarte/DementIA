# DementAI — Dementia Clinical Assistant

A multi-agent clinical decision support system for dementia care. A coordinator agent classifies each query by clinical stage and routes it to the appropriate specialist, which retrieves evidence from a medical knowledge base and responds via Claude Opus.

## Architecture

```
User query
    │
    ▼
Coordinator (LangGraph)
    │  classify stage
    ▼
┌─────────────┬────────────┬─────────────┬──────────┬──────────┐
│  Screening  │ Diagnosis  │ Prevention  │Treatment │   Care   │
└─────────────┴────────────┴─────────────┴──────────┴──────────┘
    │  each specialist retrieves from LanceDB, calls Claude Opus
    ▼
Merged response + citations
    │
    ▼
Patient record updated → Audit log
```

**Stack**

| Layer | Technology |
|---|---|
| LLM | Claude Opus 4.8 (Anthropic) |
| Agents | LangGraph StateGraph |
| Knowledge base | LanceDB + PubMedBERT embeddings |
| API | FastAPI |
| Frontend | React + Vite + Tailwind CSS |

## Clinical stages and knowledge sources

| Stage | Specialist | Sources queried |
|---|---|---|
| Screening | Screening | AAN, AWMF, Alz.org |
| Diagnosis | Diagnosis | PubMed, Neurology, AWMF |
| Prevention | Prevention | PubMed, Alz.org |
| Treatment | Treatment | PubMed, ClinicalTrials, AWMF |
| Care | Patient Care | Alz.org, AAN |

Knowledge base currently populated: **AWMF S3-Leitlinie Demenzen** (038-013, v6.1 2026) — 2,771 chunks from the Langfassung and Methodenreport.

## Setup

### Prerequisites

- Python ≥ 3.11
- Node.js ≥ 18
- An [Anthropic API key](https://console.anthropic.com/)

### 1. Clone and install

```bash
git clone git@github.com:carricarte/dementAI.git
cd dementAI

# Python backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[ingest,rag]"

# React frontend
cd frontend && npm install && cd ..
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Populate the knowledge base

```bash
python scripts/ingest.py --source awmf
```

This downloads the AWMF S3-Leitlinie Demenzen PDF (~3 MB), chunks and embeds it into LanceDB. Runtime: ~5 min on first run (downloads the PubMedBERT embedding model).

## Running

Start both servers in separate terminals:

```bash
# Backend (port 8000)
.venv/bin/uvicorn backend.main:app --reload --port 8000

# Frontend (port 3000)
cd frontend && npm run dev
```

Open **http://localhost:3000**, enter a patient ID, and submit a clinical query.

## Project structure

```
dementAI/
├── backend/
│   ├── agents/          # LangGraph specialist agents + coordinator
│   ├── api/             # FastAPI routes and Pydantic models
│   ├── audit/           # Immutable audit log writer
│   ├── rag/
│   │   ├── embedder.py  # PubMedBERT sentence-transformers wrapper
│   │   ├── retriever.py # LanceDB vector search
│   │   ├── ingestion.py # Common Document schema + ingest()
│   │   └── sources/
│   │       └── awmf.py  # AWMF REST API downloader + PDF chunker
│   ├── state/
│   │   ├── schema.py    # GraphState, PatientRecord, Citation types
│   │   └── store.py     # Patient JSON persistence
│   ├── tools/
│   │   ├── calculators.py  # Screening score calculators (MMSE, MoCA…)
│   │   └── retrieval.py    # Tool wrapper around the retriever
│   ├── config.py        # Settings (pydantic-settings, reads .env)
│   ├── llm.py           # Cached ChatAnthropic instance
│   └── main.py          # FastAPI app entry point
├── frontend/
│   └── src/
│       ├── App.tsx              # Root component; all state lives here
│       ├── api/client.ts        # fetchPatient(), submitQuery()
│       ├── types/index.ts       # TypeScript interfaces (mirrors Pydantic models)
│       └── components/
│           ├── QueryPanel.tsx   # Query input + Markdown response
│           ├── VisitHistory.tsx # Left sidebar: past visits
│           ├── PatientProfile.tsx # Right sidebar: patient record
│           ├── CitationList.tsx # Sources section
│           └── StageBadge.tsx   # Clinical stage chip
├── scripts/
│   └── ingest.py        # CLI: populate LanceDB from each source
├── tests/
├── pyproject.toml
└── .env.example
```

## Adding a new knowledge source

1. Create `backend/rag/sources/{source}.py` with a `fetch() -> list[Document]` function
2. Wire it into `scripts/ingest.py`
3. Run `python scripts/ingest.py --source {source}`

Sources planned but not yet implemented: PubMed, ClinicalTrials.gov, Neurology.org, Alz.org, AAN.

## Dementia types supported

Alzheimer's · Vascular · Lewy body · FTD-behavioral · PPA semantic · PPA nonfluent · FTD-MND · Mixed · Parkinson's dementia · Huntington's · Corticobasal degeneration · PSP · Posterior cortical atrophy · LATE (TDP-43) · CTE · Creutzfeldt-Jakob · HIV-associated · Wernicke-Korsakoff · Normal pressure hydrocephalus · Down syndrome-associated
