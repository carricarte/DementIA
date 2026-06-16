from __future__ import annotations

from backend.llm import get_llm
from backend.state.schema import GraphState
from backend.tools.retrieval import retrieve

_SYSTEM = """You are a dementia prevention specialist.
Focus on modifiable risk factors (cardiovascular, metabolic, lifestyle, sensory),
evidence-based interventions, and personalised preventive strategies.
Ground all recommendations in published evidence. Cite every factual claim."""


def run_prevention(state: GraphState) -> GraphState:
    record = state["patient_record"]
    ctx = retrieve(state["query"], source_filter=["pubmed", "alz"])

    history = _format_history(state)

    prompt = f"""{_SYSTEM}

Patient history:
{history}

Identified risk flags: {record.risk_flags or "none"}
Current medications: {record.current_medications or "none"}
Dementia type (if established): {record.dementia_type.value if record.dementia_type else "undetermined"}

Retrieved evidence:
{ctx["text"] or "(knowledge base not yet populated)"}

Physician query: {state["query"]}

Provide targeted prevention recommendations with supporting evidence."""

    response = get_llm().invoke(prompt)
    return {**state, "specialist_response": response.content, "citations": ctx["citations"]}


def _format_history(state: GraphState) -> str:
    visits = state["patient_record"].visits
    if not visits:
        return "No prior visits."
    return "\n".join(
        f"[{v.timestamp.date()} | {v.stage.value}] {v.query[:120]}"
        for v in visits[-5:]
    )
