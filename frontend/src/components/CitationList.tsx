import type { Citation } from '../types'

const SOURCE_LABELS: Record<string, string> = {
  pubmed:         'PubMed',
  clinicaltrials: 'ClinicalTrials',
  neurology:      'Neurology',
  alz:            'Alz. Association',
  aan:            'AAN',
  awmf:           'AWMF',
}

export default function CitationList({ citations }: { citations: Citation[] }) {
  if (citations.length === 0) return null

  return (
    <div className="mt-6 pt-4 border-t border-slate-200">
      <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-3">
        References
      </h4>
      <ol className="space-y-2">
        {citations.map((c, i) => (
          <li
            key={i}
            id={`ref-${i + 1}`}
            className="flex items-start gap-2.5 text-sm scroll-mt-4"
          >
            <span className="shrink-0 mt-0.5 w-6 text-right text-xs font-semibold text-slate-400">
              [{i + 1}]
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
              <span className="ml-1.5 text-xs text-slate-400">
                {SOURCE_LABELS[c.source] ?? c.source}
              </span>
              {c.pmid && (
                <a
                  href={`https://pubmed.ncbi.nlm.nih.gov/${c.pmid}`}
                  target="_blank"
                  rel="noreferrer"
                  className="ml-1.5 text-xs text-slate-400 hover:text-slate-600"
                >
                  PMID:{c.pmid}
                </a>
              )}
            </span>
          </li>
        ))}
      </ol>
    </div>
  )
}
