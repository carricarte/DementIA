import type { ReactNode } from 'react'
import type { PatientRecord, ScreeningScores } from '../types'

const DEMENTIA_LABELS: Record<string, string> = {
  alzheimers:                    "Alzheimer's Disease",
  vascular:                      'Vascular Dementia',
  lewy_body:                     'Lewy Body Dementia',
  ftd_behavioral:                'FTD (Behavioral)',
  ppa_semantic:                  'PPA — Semantic',
  ppa_nonfluent:                 'PPA — Nonfluent',
  ftd_mnd:                       'FTD-MND',
  mixed:                         'Mixed Dementia',
  parkinsons_dementia:           "Parkinson's Disease Dementia",
  huntingtons:                   "Huntington's Disease",
  corticobasal_degeneration:     'Corticobasal Degeneration',
  progressive_supranuclear_palsy:'PSP',
  posterior_cortical_atrophy:    'Posterior Cortical Atrophy',
  late_tdp43:                    'LATE (TDP-43)',
  chronic_traumatic_encephalopathy: 'CTE',
  creutzfeldt_jakob:             'Creutzfeldt-Jakob',
  hiv_dementia:                  'HIV Dementia',
  wernicke_korsakoff:            'Wernicke-Korsakoff',
  normal_pressure_hydrocephalus: 'NPH',
  down_syndrome_dementia:        'Down Syndrome Dementia',
}

function label(key: string) {
  return DEMENTIA_LABELS[key] ?? key
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="px-4 py-3 border-b border-slate-100 last:border-0">
      <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">{title}</h3>
      {children}
    </div>
  )
}

function ScoreRow({ name, value, max }: { name: string; value?: number | null; max: number }) {
  if (value == null) return null
  const pct = Math.min(100, (value / max) * 100)
  return (
    <div className="mb-2">
      <div className="flex justify-between text-xs mb-0.5">
        <span className="text-slate-500">{name}</span>
        <span className="font-medium text-slate-700">
          {value} / {max}
        </span>
      </div>
      <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
        <div
          className="h-full bg-blue-400 rounded-full transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}

function hasAnyScore(s: ScreeningScores) {
  return Object.values(s).some((v) => v != null)
}

export default function PatientProfile({ record }: { record: PatientRecord | null }) {
  return (
    <aside className="w-72 bg-white border-l border-slate-200 flex flex-col shrink-0">
      <div className="px-4 py-3 border-b border-slate-100">
        <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
          Patient Profile
        </h2>
      </div>

      <div className="flex-1 overflow-y-auto">
        {!record ? (
          <p className="px-4 py-8 text-sm text-slate-400 text-center">No record loaded</p>
        ) : (
          <>
            {/* Diagnosis */}
            <Section title="Diagnosis">
              {record.dementia_type ? (
                <p className="text-sm font-medium text-slate-800">{label(record.dementia_type)}</p>
              ) : (
                <p className="text-sm text-slate-400 italic">Undetermined</p>
              )}
              {record.differential_diagnoses.length > 0 && (
                <div className="mt-2">
                  <p className="text-xs text-slate-400 mb-1">Differentials</p>
                  {record.differential_diagnoses.map((d) => (
                    <p key={d} className="text-xs text-slate-600 leading-5">
                      · {label(d)}
                    </p>
                  ))}
                </div>
              )}
            </Section>

            {/* Scores */}
            <Section title="Screening Scores">
              {!hasAnyScore(record.screening_scores) ? (
                <p className="text-sm text-slate-400 italic">None recorded</p>
              ) : (
                <>
                  <ScoreRow name="MMSE"     value={record.screening_scores.mmse}     max={30} />
                  <ScoreRow name="MoCA"     value={record.screening_scores.moca}     max={30} />
                  <ScoreRow name="CDR"      value={record.screening_scores.cdr}      max={3}  />
                  <ScoreRow name="ADAS-Cog" value={record.screening_scores.adas_cog} max={70} />
                  <ScoreRow name="GDS"      value={record.screening_scores.gds}      max={15} />
                </>
              )}
            </Section>

            {/* Risk flags */}
            <Section title="Risk Flags">
              {record.risk_flags.length === 0 ? (
                <p className="text-sm text-slate-400 italic">None</p>
              ) : (
                <div className="flex flex-wrap gap-1.5">
                  {record.risk_flags.map((f) => (
                    <span
                      key={f}
                      className="text-xs bg-red-50 text-red-700 border border-red-100 rounded-full px-2 py-0.5"
                    >
                      {f}
                    </span>
                  ))}
                </div>
              )}
            </Section>

            {/* Medications */}
            <Section title="Medications">
              {record.current_medications.length === 0 ? (
                <p className="text-sm text-slate-400 italic">None recorded</p>
              ) : (
                <ul className="space-y-0.5">
                  {record.current_medications.map((m) => (
                    <li key={m} className="text-sm text-slate-700">
                      · {m}
                    </li>
                  ))}
                </ul>
              )}
            </Section>

            {/* Workups */}
            {(record.pending_workups.length > 0 || record.completed_workups.length > 0) && (
              <Section title="Workups">
                {record.pending_workups.map((w) => (
                  <div key={w} className="flex items-center gap-2 text-sm text-slate-700 py-0.5">
                    <span className="w-2 h-2 rounded-full bg-amber-400 shrink-0" />
                    {w}
                  </div>
                ))}
                {record.completed_workups.map((w) => (
                  <div key={w} className="flex items-center gap-2 text-sm text-slate-400 py-0.5">
                    <span className="w-2 h-2 rounded-full bg-emerald-400 shrink-0" />
                    {w}
                  </div>
                ))}
              </Section>
            )}

            <div className="px-4 py-3 text-xs text-slate-400">
              {record.visits.length} visit{record.visits.length !== 1 ? 's' : ''} ·{' '}
              ID: {record.patient_id}
            </div>
          </>
        )}
      </div>
    </aside>
  )
}
