// Small building blocks shared by the Strategy Selector panels.

const ACRONYMS = /\b(vwap|orb|rvol|atr|rsi|macd|adx|oos|pf)\b/gi

export const label = (s) =>
  s == null
    ? '—'
    : String(s)
        .replace(/_/g, ' ')
        .toLowerCase()
        .replace(/^\w/, (c) => c.toUpperCase())
        .replace(ACRONYMS, (m) => m.toUpperCase())

export const num = (v, digits = 2) => (v == null || Number.isNaN(v) ? '—' : Number(v).toFixed(digits))
export const pct = (v, digits = 1) => (v == null ? '—' : `${(Number(v) * 100).toFixed(digits)}%`)

// Tone for a regime value. Green/red stay reserved for P&L -- a bearish or
// high-volatility regime is a condition, not a loss -- so regimes read
// neutral, and only missing or untrustworthy data is called out.
export function toneOf(value) {
  const v = String(value || '').toUpperCase()
  if (/UNAVAILABLE|INSUFFICIENT|UNRELIABLE|UNKNOWN/.test(v)) return 'warn'
  return 'neutral'
}

export function Pill({ value, tone }) {
  return <span className={`ss-pill ss-pill-${tone || toneOf(value)}`}>{label(value)}</span>
}

export function FieldGrid({ rows }) {
  return (
    <dl className="ss-fields">
      {rows.map(([k, v, raw]) => (
        <div key={k} className="ss-field">
          <dt>{k}</dt>
          <dd>{raw ? <span className="ss-mono">{v}</span> : <Pill value={v} />}</dd>
        </div>
      ))}
    </dl>
  )
}

export function Panel({ title, status, children }) {
  return (
    <section className="card ss-panel">
      <header className="ss-panel-head">
        <h3 className="ss-title">{title}</h3>
        {status && <Pill value={status} tone={status === 'OK' || status === 'AVAILABLE' ? 'neutral' : undefined} />}
      </header>
      {children}
    </section>
  )
}

export function Reasons({ items }) {
  if (!items || !items.length) return null
  return (
    <details className="ss-reasons">
      <summary>Why ({items.length})</summary>
      <ul>
        {items.map((r, i) => (
          <li key={i}>{r}</li>
        ))}
      </ul>
    </details>
  )
}
