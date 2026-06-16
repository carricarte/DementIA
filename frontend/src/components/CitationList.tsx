import type { Citation } from '../types'

const SOURCE_LABELS: Record<string, string> = {
  pubmed:        'PubMed',
  clinicaltrials: 'ClinicalTrials',
  neurology:     'Neurology',
  alz:           "Alz. Association",
  aan:           'AAN',
  awmf:          'AWMF',
}

export default function CitationList({ citations }: { citations: Citation[] }) {
  if (citations.length === 0) return null

  return (
    <div className="mt-5 pt-4 border-t border-slate-100">
      <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">
        Sources ({citations.length})
      </h4>
      <ul className="space-y-2">
        {citations.map((c, i) => (
          <li key={i} className="flex items-start gap-2 text-sm">
            <span className="shrink-0 mt-0.5 text-xs bg-slate-100 text-slate-500 rounded px-1.5 py-0.5 font-medium">
              {SOURCE_LABELS[c.source] ?? c.source}
            </span>
            <span className="leading-snug">
              {c.url ? (
                <a
                  href={c.url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  {c.title}
                </a>
              ) : (
                <span className="text-slate-700">{c.title}</span>
              )}
              {c.pmid && (
                <a
                  href={`https://pubmed.ncbi.nlm.nih.gov/${c.pmid}`}
                  target="_blank"
                  rel="noreferrer"
                  className="ml-2 text-slate-400 hover:text-slate-600 text-xs"
                >
                  PMID:{c.pmid}
                </a>
              )}
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}
