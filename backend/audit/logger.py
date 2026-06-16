from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from backend.config import settings


class AuditLogger:
    def __init__(self) -> None:
        self._root = Path(settings.audit_log_path)
        self._root.mkdir(parents=True, exist_ok=True)

    def log(self, state: dict) -> None:
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "patient_id": state.get("patient_id"),
            "stage": state.get("stage"),
            "query": state.get("query"),
            "citation_count": len(state.get("citations", [])),
        }
        log_file = self._root / f"{state.get('patient_id', 'unknown')}.jsonl"
        with log_file.open("a") as f:
            f.write(json.dumps(entry) + "\n")


audit_logger = AuditLogger()
