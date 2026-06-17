import type { Citation, ClinicalStage, PatientRecord, QueryRequest, QueryResponse } from '../types'

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

export async function streamQuery(
  req: QueryRequest,
  onStage: (stage: ClinicalStage) => void,
  onChunk: (text: string) => void,
  onDone: (citations: Citation[]) => void,
): Promise<void> {
  const res = await fetch('/query/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`)

  const reader = res.body!.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    // SSE events are separated by double newlines
    const parts = buffer.split('\n\n')
    buffer = parts.pop() ?? ''

    for (const part of parts) {
      const line = part.trim()
      if (!line.startsWith('data: ')) continue
      const event = JSON.parse(line.slice(6))
      if (event.type === 'stage') onStage(event.stage as ClinicalStage)
      else if (event.type === 'chunk') onChunk(event.text as string)
      else if (event.type === 'done') onDone(event.citations as Citation[])
      else if (event.type === 'error') throw new Error(event.message as string)
    }
  }
}
