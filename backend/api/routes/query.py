from fastapi import APIRouter, HTTPException

from backend.agents.coordinator import coordinator
from backend.api.models import QueryRequest, QueryResponse
from backend.state.schema import GraphState

router = APIRouter()


@router.post("/", response_model=QueryResponse)
def handle_query(req: QueryRequest) -> QueryResponse:
    initial: GraphState = {
        "patient_id": req.patient_id,
        "query": req.query,
        "stage": None,
        "patient_record": None,
        "specialist_response": None,
        "citations": [],
        "final_response": None,
    }
    try:
        result = coordinator.invoke(initial)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return QueryResponse(
        patient_id=req.patient_id,
        stage=result["stage"],
        response=result["final_response"] or "",
        citations=result["citations"],
    )
