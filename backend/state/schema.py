from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import TypedDict

from pydantic import BaseModel, Field


class ClinicalStage(str, Enum):
    SCREENING = "screening"
    DIAGNOSIS = "diagnosis"
    PREVENTION = "prevention"
    TREATMENT = "treatment"
    CARE = "care"


class DementiaType(str, Enum):
    ALZHEIMERS = "alzheimers"
    VASCULAR = "vascular"
    LEWY_BODY = "lewy_body"
    FTD_BEHAVIORAL = "ftd_behavioral"
    PPA_SEMANTIC = "ppa_semantic"
    PPA_NONFLUENT = "ppa_nonfluent"
    FTD_MND = "ftd_mnd"
    MIXED = "mixed"
    PARKINSONS_DEMENTIA = "parkinsons_dementia"
    HUNTINGTONS = "huntingtons"
    CORTICOBASAL = "corticobasal_degeneration"
    PSP = "progressive_supranuclear_palsy"
    POSTERIOR_CORTICAL = "posterior_cortical_atrophy"
    LATE = "late_tdp43"
    CTE = "chronic_traumatic_encephalopathy"
    CJD = "creutzfeldt_jakob"
    HIV_DEMENTIA = "hiv_dementia"
    WERNICKE_KORSAKOFF = "wernicke_korsakoff"
    NPH = "normal_pressure_hydrocephalus"
    DOWN_SYNDROME = "down_syndrome_dementia"


class Citation(BaseModel):
    source: str  # pubmed | clinicaltrials | neurology | alz | aan | awmf
    title: str
    url: str | None = None
    pmid: str | None = None


class ScreeningScores(BaseModel):
    mmse: int | None = None       # 0–30
    moca: int | None = None       # 0–30
    cdr: float | None = None      # 0, 0.5, 1, 2, 3
    adas_cog: float | None = None # 0–70
    gds: int | None = None        # Geriatric Depression Scale short form 0–15


class VisitRecord(BaseModel):
    visit_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    stage: ClinicalStage
    query: str
    specialist_response: str
    citations: list[Citation] = Field(default_factory=list)


class PatientRecord(BaseModel):
    patient_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    dementia_type: DementiaType | None = None
    differential_diagnoses: list[DementiaType] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)

    screening_scores: ScreeningScores = Field(default_factory=ScreeningScores)
    current_medications: list[str] = Field(default_factory=list)

    completed_workups: list[str] = Field(default_factory=list)
    pending_workups: list[str] = Field(default_factory=list)

    visits: list[VisitRecord] = Field(default_factory=list)


# Flows through the LangGraph coordinator for one interaction
class GraphState(TypedDict):
    patient_id: str
    query: str
    stage: ClinicalStage | None
    patient_record: PatientRecord | None
    specialist_response: str | None
    citations: list[Citation]
    final_response: str | None
