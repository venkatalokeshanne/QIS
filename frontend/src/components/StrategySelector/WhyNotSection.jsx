import { useMemo, useState } from 'react'
import { label } from './shared'

// Groups every non-qualified strategy by the gate that stopped it, closest
// miss first, so "why not X?" is answerable at a glance.
const ORDER = [
  'NOT_QUALIFIED',
  'NOT_EVALUATED',
  'FAMILY_NOT_APPLICABLE',
  'DATA_UNAVAILABLE',
  'TIMEFRAME_MISMATCH',
  'DATA_MISMATCH',
  'NOT_APPLICABLE',
  'NOT_RUNNABLE',
]

export default function WhyNotSection({ rejected }) {
  const [filter, setFilter] = useState('')
  const groups = useMemo(() => {
    const q = filter.trim().toLowerCase()
    const g = {}
    for (const r of rejected) {
      if (q && !r.strategy.toLowerCase().includes(q)) continue
      if (!g[r.status]) g[r.status] = []
      g[r.status].push(r)
    }
    return [...ORDER, ...Object.keys(g).filter((k) => !ORDER.includes(k))]
      .filter((k) => g[k])
      .map((k) => [k, g[k]])
  }, [rejected, filter])

  return (
    <section className="card ss-panel">
      <header className="ss-panel-head">
        <h3 className="ss-title">Why not the others ({rejected.length})</h3>
        <input
          className="field-input ss-filter"
          placeholder="Find a strategy"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          aria-label="Filter rejected strategies"
        />
      </header>
      {groups.map(([status, items]) => (
        <details key={status} className="ss-group" open={status === 'NOT_QUALIFIED' || !!filter}>
          <summary>
            <span>{label(status)}</span>
            <span className="ss-mono ss-count">{items.length}</span>
          </summary>
          <ul>
            {items.map((r) => (
              <li key={r.strategy_id}>
                <span className="ss-strat">{r.strategy}</span>
                <span className="ss-meta">{r.reason}</span>
              </li>
            ))}
          </ul>
        </details>
      ))}
      {!groups.length && <p className="ss-meta">No strategy matches “{filter}”.</p>}
    </section>
  )
}
