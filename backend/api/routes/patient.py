from fastapi import APIRouter, HTTPException

from backend.api.models import PatientResponse
from backend.state.store import patient_store

router = APIRouter()


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: str) -> PatientResponse:
    record = patient_store.load(patient_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return PatientResponse(record=record)


@router.delete("/{patient_id}")
def delete_patient(patient_id: str) -> dict:
    p = patient_store._path(patient_id)
    if not p.exists():
        raise HTTPException(status_code=404, detail="Patient not found")
    p.unlink()
    return {"deleted": patient_id}
