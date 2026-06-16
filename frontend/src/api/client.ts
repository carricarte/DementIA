import type { PatientRecord, QueryRequest, QueryResponse } from '../types'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${await res.text()}`)
  }
  return res.json()
}

export async function fetchPatient(patientId: string): Promise<PatientRecord> {
  const data = await request<{ record: PatientRecord }>(
    `/patient/${encodeURIComponent(patientId)}`
  )
  return data.record
}

export async function submitQuery(req: QueryRequest): Promise<QueryResponse> {
  return request<QueryResponse>('/query/', {
    method: 'POST',
    body: JSON.stringify(req),
  })
}
