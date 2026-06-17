from __future__ import annotations

from backend.llm import get_llm
from backend.prompts import load
from backend.state.schema import Citation, GraphState
from backend.tools.retrieval import retrieve

_SYSTEM = load("diagnosis")


def prepare(state: GraphState) -> tuple[str, list[Citation]]:
    """Returns (prompt, citations) without invoking the LLM."""
    record = state["patient_record"]
    ctx = retrieve(state["query"], source_filter=["pubmed", "neurology", "awmf"])

    differentials = [d.value for d in record.differential_diagnoses]
    history = _format_history(state)

    prompt = f"""{_SYSTEM}

Patient history:
{history}

Current diagnosis: {record.dementia_type.value if record.dementia_type else "undetermined"}
Differential diagnoses under consideration: {differentials or "none established"}
Screening scores: {record.screening_scores.model_dump(exclude_none=True) or "not available"}
Completed workups: {record.completed_workups or "none"}
Pending workups: {record.pending_workups or "none"}

Retrieved evidence:
{ctx["text"] or "(knowledge base not yet populated)"}

Physician query: {state["query"]}

Provide a diagnostic assessment. If a subtype can be suggested, name it and rate your
confidence (low / moderate / high) with supporting evidence."""

    return prompt, ctx["citations"]


def run_diagnosis(state: GraphState) -> GraphState:
    prompt, citations = prepare(state)
    response = get_llm().invoke(prompt)
    return {**state, "specialist_response": response.content, "citations": citations}


def _format_history(state: GraphState) -> str:
    visits = state["patient_record"].visits
    if not visits:
        return "No prior visits."
    return "\n".join(
        f"[{v.timestamp.date()} | {v.stage.value}] {v.query[:120]}" for v in visits[-5:]
    )
