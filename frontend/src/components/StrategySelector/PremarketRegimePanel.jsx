import { FieldGrid, Panel, Reasons, num, pct } from './shared'

export default function PremarketRegimePanel({ regime, included }) {
  if (!included) {
    return (
      <Panel title="Premarket" status="EXCLUDED">
        <p className="ss-meta">Premarket analysis was turned off for this request.</p>
      </Panel>
    )
  }
  if (!regime) return null
  return (
    <Panel title="Premarket" status={regime.status}>
      <div className="ss-headline">{regime.regime ? regime.regime.replace(/_/g, ' ') : '—'}</div>
      <FieldGrid
        rows={[
          ['Direction', regime.direction],
          ['Change', pct(regime.change_pct, 2), true],
          ['Structure', regime.structure],
          ['Volume', regime.volume],
          ['Premarket RVOL', num(regime.premarket_rvol), true],
          ['Liquidity', regime.liquidity],
          ['Reliability', regime.reliability],
          ['Catalyst', regime.catalyst],
          ['Confidence', num(regime.confidence, 0), true],
        ]}
      />
      <p className="ss-meta">Data through {regime.data_through || '—'} (frozen at the 09:30 open)</p>
      <Reasons items={regime.reasons} />
    </Panel>
  )
}
