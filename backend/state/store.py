from pathlib import Path

from backend.config import settings
from backend.state.schema import PatientRecord


class PatientStore:
    def __init__(self, path: str = settings.patient_store_path):
        self._root = Path(path)
        self._root.mkdir(parents=True, exist_ok=True)

    def _path(self, patient_id: str) -> Path:
        return self._root / f"{patient_id}.json"

    def load(self, patient_id: str) -> PatientRecord | None:
        p = self._path(patient_id)
        if not p.exists():
            return None
        return PatientRecord.model_validate_json(p.read_text())

    def save(self, record: PatientRecord) -> None:
        self._path(record.patient_id).write_text(record.model_dump_json(indent=2))

    def create(self, patient_id: str) -> PatientRecord:
        record = PatientRecord(patient_id=patient_id)
        self.save(record)
        return record

    def load_or_create(self, patient_id: str) -> PatientRecord:
        return self.load(patient_id) or self.create(patient_id)


patient_store = PatientStore()
