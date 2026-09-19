import { FieldGrid, Panel, Reasons, num } from './shared'

export default function MarketRegimePanel({ regime }) {
  if (!regime) return null
  return (
    <Panel title="Market regime" status={regime.status}>
      <div className="ss-headline">{regime.regime ? regime.regime.replace(/_/g, ' ') : '—'}</div>
      <FieldGrid
        rows={[
          ['Direction', regime.direction],
          ['Trend strength', regime.trend_strength],
          ['Volatility', regime.volatility],
          ['Breadth', regime.breadth],
          ['Market premarket', regime.market_premarket],
          ['Confidence', num(regime.confidence, 0), true],
        ]}
      />
      {regime.symbols && (
        <dl className="ss-fields">
          {Object.entries(regime.symbols).map(([sym, s]) => (
            <div key={sym} className="ss-field">
              <dt className="ss-mono">{sym}</dt>
              <dd className="ss-meta">
                {s.direction ?? '—'} · structure {s.structure ?? '—'} · ADX {num(s.adx, 1)}
              </dd>
            </div>
          ))}
        </dl>
      )}
      <p className="ss-meta">As of {regime.as_of || '—'}</p>
      <Reasons items={regime.reasons} />
    </Panel>
  )
}
