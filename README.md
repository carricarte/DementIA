# DementIA — AI-powered dementia clinical decision support

A multi-agent clinical decision support system for dementia care. A coordinator classifies the query by clinical stage and routes it to the appropriate specialist agent. When patient data is provided, an analyzer agent first produces a structured clinical summary that the specialist uses as context.

## Architecture

```
          user query
               │
               ▼
     coordinator agent
     classifies clinical stage
               │
               ▼
     patient data provided?
          │         │
         no        yes
          │         │
          │         ▼
          │   analyzer agent
          │   reads patient record
          │   produces clinical summary
          │         │
          └────┬────┘
               │
               ▼
     specialist agent (by stage)
     retrieve clinical evidence
     generate grounded response
               │
               ▼
     response + references
     (patient-specific when patient data provided)
```

**SSE stream events:**

| Event | Field |
|---|---|
| `{"type":"stage","stage":"..."}` | classified clinical stage |
| `{"type":"chunk","text":"..."}` | streaming response token |
| `{"type":"done","citations":[...],"personalized":bool}` | final metadata |

**Stack**

| Layer | Technology |
|---|---|
| LLM | Claude Opus 4.8 (Anthropic) |
| Agents | LangGraph StateGraph |
| Knowledge base | LanceDB + PubMedBERT embeddings (768-dim) |
| Research data | NACC UDS, MRI scan, genetics CSVs (synthetic) |
| API | FastAPI — `POST /query`, `POST /query/stream` |
| Frontend | React + Vite + Tailwind CSS |

## Agents

### Coordinator
Classifies the query by clinical stage, then routes based on what the user provides:
- **No patient data** — routes directly to the stage specialist.
- **Patient data provided** — invokes the Analyzer Agent first, then passes its clinical summary to the stage specialist.

### Analyzer Agent
Reads the patient record (clinical history + research data) and produces a structured clinical summary — diagnosis stage, cognitive scores, risk factors, medications, MRI findings, and ranked treatment priorities. Its output is passed to the specialist as context; patient data never enters the knowledge base.

### Specialist Agents
Always generate the final response. Retrieve clinical evidence from a stage-specific subset of the knowledge base and build a grounded answer — using the analyzer's clinical summary as additional context when patient data was provided.

| Stage | Specialist | Source filters |
|---|---|---|
| Screening | Screening | `aan`, `awmf`, `alz` |
| Diagnosis | Diagnosis | `pubmed`, `neurology`, `awmf` |
| Prevention | Prevention | `pubmed`, `alz` |
| Treatment | Treatment | `pubmed`, `clinicaltrials`, `awmf` |
| Care | Patient Care | `alz`, `aan` |

## Knowledge base

Currently populated:

| Source | Status | Chunks |
|---|---|---|
| AWMF S3-Leitlinie Demenzen (038-013, v6.1 2026) | ✅ | ~2,771 |
| PubMed (NCBI E-utilities) | ✅ | ~4,130 |
| ClinicalTrials.gov | not yet implemented | — |
| Neurology.org | not yet implemented | — |
| Alz.org | not yet implemented | — |
| AAN.com | not yet implemented | — |

## Setup

### Prerequisites

- Python ≥ 3.11
- Node.js ≥ 18
- An [Anthropic API key](https://console.anthropic.com/)

### 1. Clone and install

```bash
git clone git@github.com:carricarte/DementIA.git
cd DementIA

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
python scripts/ingest.py --source pubmed
```

Runtime: ~5 min on first run (downloads the PubMedBERT embedding model).

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
DementIA/
├── backend/
│   ├── agents/
│   │   ├── coordinator.py   # LangGraph graph; classify_stage → classify_intent → branch
│   │   ├── analyzer.py      # Analyzer Agent: PatientStore + NACC UDS → PatientStatusReport
│   │   ├── screening.py
│   │   ├── diagnosis.py
│   │   ├── prevention.py
│   │   ├── treatment.py
│   │   └── care.py
│   ├── api/
│   │   ├── routes/
│   │   │   ├── query.py     # POST /query, POST /query/stream
│   │   │   └── patient.py   # Patient CRUD
│   │   └── models.py        # QueryRequest, QueryResponse (personalized field)
│   ├── audit/               # Append-only JSONL audit writer
│   ├── rag/
│   │   ├── embedder.py      # PubMedBERT sentence-transformers wrapper
│   │   ├── retriever.py     # LanceDB vector search + enrich_query
│   │   ├── chunker.py       # Token-aware sentence chunker (512 tokens)
│   │   ├── ingestion.py     # Document dataclass + ingest()
│   │   └── sources/
│   │       ├── awmf.py      # AWMF REST API downloader + PDF chunker
│   │       └── pubmed.py    # NCBI E-utilities fetcher
│   ├── state/
│   │   ├── schema.py        # GraphState, PatientRecord, PatientStatusReport, Citation
│   │   └── store.py         # PatientStore — JSON persistence under data/patients/
│   ├── tools/
│   │   ├── calculators.py   # Screening score calculators (MMSE, MoCA, CDR…)
│   │   └── retrieval.py     # retrieve() + enrich_query() wrappers
│   ├── config.py            # Settings (pydantic-settings, reads .env)
│   ├── llm.py               # Cached ChatAnthropic singleton
│   └── main.py              # FastAPI app entry point
├── frontend/
│   └── src/
│       ├── App.tsx              # Root component; owns patient ID, record, response
│       ├── api/client.ts        # fetchPatient(), streamQuery() — SSE event handling
│       ├── types/index.ts       # TypeScript interfaces (mirrors Pydantic models)
│       └── components/
│           ├── QueryPanel.tsx   # Query input + streaming Markdown response
│           ├── VisitHistory.tsx # Left sidebar: past visits
│           ├── PatientProfile.tsx # Right sidebar: patient record
│           ├── CitationList.tsx # Numbered references section
│           └── StageBadge.tsx   # Clinical stage chip
├── scripts/
│   └── ingest.py            # CLI: populate LanceDB from each source
├── data/
│   ├── lancedb/             # Vector store (gitignored)
│   ├── patients/            # Patient JSON records (gitignored)
│   ├── audit/               # Audit JSONL (gitignored)
│   └── synthetic/           # NACC UDS / MRI / genetics CSVs (gitignored)
├── tests/
├── pyproject.toml
└── .env.example
```

## Adding a new knowledge source

1. Create `backend/rag/sources/{source}.py` with a `fetch() -> list[Document]` function
2. Wire it into `scripts/ingest.py`
3. Run `python scripts/ingest.py --source {source}`

Valid `source_filter` values: `awmf`, `pubmed`, `clinicaltrials`, `neurology`, `alz`, `aan`.

## Dementia types supported (20)

Alzheimer's · Vascular · Lewy body · FTD-behavioral · PPA semantic · PPA nonfluent · FTD-MND · Mixed · Parkinson's dementia · Huntington's · Corticobasal degeneration · PSP · Posterior cortical atrophy · LATE (TDP-43) · CTE · Creutzfeldt-Jakob · HIV-associated · Wernicke-Korsakoff · Normal pressure hydrocephalus · Down syndrome-associated
