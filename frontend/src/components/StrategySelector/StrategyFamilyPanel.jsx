import { Panel, label } from './shared'

export default function StrategyFamilyPanel({ eligible = [], lowerPriority = [], rules = [], notes = [] }) {
  return (
    <Panel title="Strategy families">
      <div className="ss-chips">
        {eligible.map((f) => (
          <span key={f} className="ss-pill ss-pill-accent">{label(f)}</span>
        ))}
        {lowerPriority.map((f) => (
          <span key={f} className="ss-pill ss-pill-dim" title="Lower priority in this regime">{label(f)}</span>
        ))}
        {!eligible.length && !lowerPriority.length && <span className="ss-meta">No family applies.</span>}
      </div>
      <p className="ss-meta">Highlighted = eligible · dimmed = lower priority</p>
      {rules.length > 0 && (
        <ul className="ss-rules">
          {rules.map((r) => (
            <li key={r.name}>
              <span className="ss-mono">{r.name}</span>
              <span className="ss-meta">
                {Object.entries(r.when || {})
                  .map(([k, v]) => `${k} ∈ {${(Array.isArray(v) ? v : [v]).join(', ')}}`)
                  .join(' and ')}
              </span>
            </li>
          ))}
        </ul>
      )}
      {notes.map((n, i) => (
        <p key={i} className="ss-meta">{n}</p>
      ))}
    </Panel>
  )
}
