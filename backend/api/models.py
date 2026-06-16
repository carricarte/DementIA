from pydantic import BaseModel

from backend.state.schema import Citation, ClinicalStage, PatientRecord


class QueryRequest(BaseModel):
    patient_id: str
    query: str


class QueryResponse(BaseModel):
    patient_id: str
    stage: ClinicalStage
    response: str
    citations: list[Citation]


class PatientResponse(BaseModel):
    record: PatientRecord
