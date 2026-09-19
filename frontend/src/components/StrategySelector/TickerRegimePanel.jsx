import { FieldGrid, Panel, Reasons, num } from './shared'

export default function TickerRegimePanel({ ticker, regime }) {
  if (!regime) return null
  const warnings = regime.warnings || []
  return (
    <Panel title={`${ticker} regime`} status={regime.status}>
      <div className="ss-headline">{regime.regime ? regime.regime.replace(/_/g, ' ') : '—'}</div>
      <FieldGrid
        rows={[
          ['Trend', regime.trend],
          ['Momentum', regime.momentum],
          ['Relative strength', regime.relative_strength],
          ['Volatility', regime.volatility],
          ['Volume', regime.volume],
          ['Gap', regime.gap],
          ['Liquidity', regime.liquidity],
          ['Events', regime.event_status],
          ['Confidence', num(regime.confidence, 0), true],
        ]}
      />
      {warnings.length > 0 && <p className="ss-warn">{warnings.join(' · ')}</p>}
      <p className="ss-meta">As of {regime.as_of || '—'}</p>
      <Reasons items={regime.reasons} />
    </Panel>
  )
}
