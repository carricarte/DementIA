import type { VisitRecord } from '../types'
import StageBadge from './StageBadge'

function fmtDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

interface Props {
  visits: VisitRecord[]
  onSelect?: (visit: VisitRecord) => void
}

export default function VisitHistory({ visits, onSelect }: Props) {
  const reversed = [...visits].reverse()

  return (
    <aside className="w-60 bg-white border-r border-slate-200 flex flex-col shrink-0">
      <div className="px-4 py-3 border-b border-slate-100">
        <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
          Visit History
        </h2>
      </div>

      <div className="flex-1 overflow-y-auto">
        {reversed.length === 0 ? (
          <p className="px-4 py-8 text-sm text-slate-400 text-center">No prior visits</p>
        ) : (
          <ul>
            {reversed.map((visit) => (
              <li
                key={visit.visit_id}
                onClick={() => onSelect?.(visit)}
                className={`px-4 py-3 border-b border-slate-50 transition-colors ${
                  onSelect ? 'cursor-pointer hover:bg-slate-50' : ''
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <StageBadge stage={visit.stage} />
                  <span className="text-xs text-slate-400">{fmtDate(visit.timestamp)}</span>
                </div>
                <p className="text-xs text-slate-500 mt-1 line-clamp-2 leading-relaxed">
                  {visit.query}
                </p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </aside>
  )
}
