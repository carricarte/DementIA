export type ClinicalStage = 'screening' | 'diagnosis' | 'prevention' | 'treatment' | 'care';

export interface Citation {
  source: string;
  title: string;
  url?: string;
  pmid?: string;
}

export interface ScreeningScores {
  mmse?: number | null;
  moca?: number | null;
  cdr?: number | null;
  adas_cog?: number | null;
  gds?: number | null;
}

export interface VisitRecord {
  visit_id: string;
  timestamp: string;
  stage: ClinicalStage;
  query: string;
  specialist_response: string;
  citations: Citation[];
}

export interface PatientRecord {
  patient_id: string;
  created_at: string;
  updated_at: string;
  dementia_type?: string | null;
  differential_diagnoses: string[];
  risk_flags: string[];
  screening_scores: ScreeningScores;
  current_medications: string[];
  completed_workups: string[];
  pending_workups: string[];
  visits: VisitRecord[];
}

export interface QueryRequest {
  patient_id: string;
  query: string;
}

export interface QueryResponse {
  patient_id: string;
  stage: ClinicalStage;
  response: string;
  citations: Citation[];
}
