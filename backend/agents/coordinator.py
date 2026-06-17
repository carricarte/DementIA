from __future__ import annotations

import json
from typing import Iterator

from langgraph.graph import END, StateGraph

from backend.audit.logger import audit_logger
from backend.llm import get_llm
from backend.prompts import load
from backend.state.schema import ClinicalStage, GraphState, PatientRecord, VisitRecord
from backend.state.store import patient_store

from . import care as _care
from . import diagnosis as _diagnosis
from . import prevention as _prevention
from . import screening as _screening
from . import treatment as _treatment
from .care import run_care
from .diagnosis import run_diagnosis
from .prevention import run_prevention
from .screening import run_screening
from .treatment import run_treatment

_CLASSIFY_PROMPT = load("coordinator_classify")


def classify_stage(state: GraphState) -> GraphState:
    response = get_llm().invoke(_CLASSIFY_PROMPT.format(query=state["query"]))
    raw = response.content.strip().lower().split()[0]
    try:
        stage = ClinicalStage(raw)
    except ValueError:
        stage = ClinicalStage.SCREENING
    return {**state, "stage": stage}


def load_patient(state: GraphState) -> GraphState:
    record = patient_store.load_or_create(state["patient_id"])
    return {**state, "patient_record": record}


def route_to_specialist(state: GraphState) -> str:
    return state["stage"].value


def merge_output(state: GraphState) -> GraphState:
    # Single-specialist path: final_response == specialist_response.
    # Extend here to merge multiple specialists if needed.
    return {**state, "final_response": state["specialist_response"]}


def save_state(state: GraphState) -> GraphState:
    record: PatientRecord = state["patient_record"]
    record.visits.append(
        VisitRecord(
            stage=state["stage"],
            query=state["query"],
            specialist_response=state["specialist_response"] or "",
            citations=state["citations"],
        )
    )
    patient_store.save(record)
    return state


def audit_log(state: GraphState) -> GraphState:
    audit_logger.log(state)
    return state


_PREPARE_MAP = {
    ClinicalStage.SCREENING: lambda s: _screening.prepare(s),
    ClinicalStage.DIAGNOSIS: lambda s: _diagnosis.prepare(s),
    ClinicalStage.PREVENTION: lambda s: _prevention.prepare(s),
    ClinicalStage.TREATMENT: lambda s: _treatment.prepare(s),
    ClinicalStage.CARE: lambda s: _care.prepare(s),
}


def stream_query(patient_id: str, query: str) -> Iterator[str]:
    """Yield SSE-formatted lines for a streaming query response."""
    state: GraphState = {
        "patient_id": patient_id,
        "query": query,
        "stage": None,
        "patient_record": None,
        "specialist_response": None,
        "citations": [],
        "final_response": None,
    }

    try:
        state = classify_stage(state)
    except Exception as exc:
        yield f"data: {json.dumps({'type': 'error', 'message': str(exc)})}\n\n"
        return

    yield f"data: {json.dumps({'type': 'stage', 'stage': state['stage'].value})}\n\n"
    state = load_patient(state)

    try:
        prompt, citations = _PREPARE_MAP[state["stage"]](state)
    except Exception as exc:
        yield f"data: {json.dumps({'type': 'error', 'message': str(exc)})}\n\n"
        return

    full_response = ""
    try:
        for chunk in get_llm().stream(prompt):
            text = chunk.content
            if text:
                full_response += text
                yield f"data: {json.dumps({'type': 'chunk', 'text': text})}\n\n"
    except Exception as exc:
        yield f"data: {json.dumps({'type': 'error', 'message': str(exc)})}\n\n"
        return

    state = {
        **state,
        "specialist_response": full_response,
        "citations": citations,
        "final_response": full_response,
    }
    try:
        save_state(state)
        audit_log(state)
    except Exception:
        pass  # persistence errors must not break the stream

    done_payload = json.dumps({"type": "done", "citations": [c.model_dump() for c in citations]})
    yield f"data: {done_payload}\n\n"


def build_graph():
    g = StateGraph(GraphState)

    g.add_node("classify_stage", classify_stage)
    g.add_node("load_patient", load_patient)
    g.add_node(ClinicalStage.SCREENING.value, run_screening)
    g.add_node(ClinicalStage.DIAGNOSIS.value, run_diagnosis)
    g.add_node(ClinicalStage.PREVENTION.value, run_prevention)
    g.add_node(ClinicalStage.TREATMENT.value, run_treatment)
    g.add_node(ClinicalStage.CARE.value, run_care)
    g.add_node("merge_output", merge_output)
    g.add_node("save_state", save_state)
    g.add_node("audit_log", audit_log)

    g.set_entry_point("classify_stage")
    g.add_edge("classify_stage", "load_patient")
    g.add_conditional_edges(
        "load_patient",
        route_to_specialist,
        {s.value: s.value for s in ClinicalStage},
    )
    for stage in ClinicalStage:
        g.add_edge(stage.value, "merge_output")
    g.add_edge("merge_output", "save_state")
    g.add_edge("save_state", "audit_log")
    g.add_edge("audit_log", END)

    return g.compile()


coordinator = build_graph()
