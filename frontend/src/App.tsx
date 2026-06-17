import { useState, useCallback } from 'react'
import type { PatientRecord, QueryResponse, VisitRecord } from './types'
import { fetchPatient, streamQuery } from './api/client'
import VisitHistory from './components/VisitHistory'
import QueryPanel from './components/QueryPanel'
import PatientProfile from './components/PatientProfile'

export default function App() {
  const [patientIdInput, setPatientIdInput] = useState('')
  const [activeId, setActiveId] = useState('')
  const [record, setRecord] = useState<PatientRecord | null>(null)
  const [response, setResponse] = useState<QueryResponse | null>(null)
  const [selectedVisit, setSelectedVisit] = useState<VisitRecord | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isStreaming, setIsStreaming] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadPatient = useCallback(async (id: string) => {
    const trimmed = id.trim()
    if (!trimmed) return
    setError(null)
    setResponse(null)
    setSelectedVisit(null)
    setActiveId(trimmed)
    try {
      const r = await fetchPatient(trimmed)
      setRecord(r)
    } catch (e) {
      if (!(e instanceof Error && e.message.includes('404'))) {
        setError('Backend unreachable — start uvicorn to enable queries.')
      }
      setRecord(null)
    }
  }, [])

  const handleQuery = async (query: string) => {
    if (!activeId) return
    setIsLoading(true)
    setIsStreaming(false)
    setError(null)
    setSelectedVisit(null)
    setResponse(null)

    try {
      await streamQuery(
        { patient_id: activeId, query },
        (stage) => {
          setResponse({ patient_id: activeId, stage, response: '', citations: [] })
        },
        (text) => {
          setIsLoading(false)
          setIsStreaming(true)
          setResponse(prev =>
            prev ? { ...prev, response: prev.response + text } : null
          )
        },
        (citations) => {
          setIsStreaming(false)
          setResponse(prev => (prev ? { ...prev, citations } : null))
          fetchPatient(activeId).then(setRecord).catch(() => {})
        },
      )
    } catch (e) {
      setIsStreaming(false)
      setIsLoading(false)
      setError(e instanceof Error ? e.message : 'Query failed — is the backend running?')
    }
  }

  const handleVisitSelect = (visit: VisitRecord) => {
    setSelectedVisit(visit)
    setResponse(null)
  }

  return (
    <div className="h-screen flex flex-col bg-slate-100">

      {/* ── Header ─────────────────────────────────────────────── */}
      <header className="bg-slate-900 text-white px-6 py-3 flex items-center gap-8 shadow-lg shrink-0">
        <div className="shrink-0">
          <p className="text-base font-semibold tracking-tight leading-none">DCA</p>
          <p className="text-xs text-slate-400 mt-0.5">Dementia Clinical Assistant</p>
        </div>

        <div className="flex items-center gap-2">
          <label className="text-xs text-slate-400 shrink-0">Patient ID</label>
          <input
            className="bg-slate-800 border border-slate-600 rounded-lg px-3 py-1.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-400 w-48 transition-colors"
            placeholder="Enter ID…"
            value={patientIdInput}
            onChange={(e) => setPatientIdInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && loadPatient(patientIdInput)}
          />
          <button
            className="bg-blue-600 hover:bg-blue-500 text-white text-sm px-4 py-1.5 rounded-lg transition-colors font-medium"
            onClick={() => loadPatient(patientIdInput)}
          >
            Load
          </button>
        </div>

        {activeId && (
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <span className="text-slate-200 font-medium">{activeId}</span>
            {!record && (
              <span className="text-xs bg-slate-700 rounded px-2 py-0.5">new patient</span>
            )}
          </div>
        )}
      </header>

      {/* ── Body ───────────────────────────────────────────────── */}
      {activeId ? (
        <div className="flex flex-1 overflow-hidden">
          <VisitHistory
            visits={record?.visits ?? []}
            onSelect={handleVisitSelect}
          />
          <main className="flex-1 overflow-hidden">
            <QueryPanel
              onQuery={handleQuery}
              isLoading={isLoading}
              isStreaming={isStreaming}
              response={response}
              selectedVisit={selectedVisit}
              error={error}
            />
          </main>
          <PatientProfile record={record} />
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center text-slate-400">
            <p className="text-2xl font-light">Enter a patient ID to begin</p>
            <p className="text-sm mt-2">New patients are created automatically on first query</p>
          </div>
        </div>
      )}
    </div>
  )
}
