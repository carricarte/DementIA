from __future__ import annotations

from backend.llm import get_llm
from backend.prompts import load
from backend.state.schema import Citation, GraphState
from backend.tools.retrieval import retrieve

_SYSTEM = load("prevention")


def prepare(state: GraphState) -> tuple[str, list[Citation]]:
    """Returns (prompt, citations) without invoking the LLM."""
    record = state["patient_record"]
    ctx = retrieve(state["query"], source_filter=["pubmed", "alz"])

    history = _format_history(state)
    dementia_type = record.dementia_type.value if record.dementia_type else "undetermined"

    prompt = f"""{_SYSTEM}

Patient history:
{history}

Identified risk flags: {record.risk_flags or "none"}
Current medications: {record.current_medications or "none"}
Dementia type (if established): {dementia_type}

Retrieved evidence:
{ctx["text"] or "(knowledge base not yet populated)"}

Physician query: {state["query"]}

Provide targeted prevention recommendations with supporting evidence."""

    return prompt, ctx["citations"]


def run_prevention(state: GraphState) -> GraphState:
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
