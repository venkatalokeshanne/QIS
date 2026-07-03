import MetricValue from './MetricValue'
import { formatDateTime } from '../utils/format'
import './TradesTable.css'

// entry_price is per-unit, quantity is the position size -- the trade's
// cost basis is their product, so pnl / cost basis gives the % return
// regardless of direction (pnl is already signed correctly for shorts).
function pnlPct(trade) {
  const costBasis = trade.entry_price * trade.quantity
  if (!costBasis || trade.pnl === null || trade.pnl === undefined) return null
  return (trade.pnl / costBasis) * 100
}

function resultLabel(pnl) {
  if (pnl === null || pnl === undefined || pnl === 0) return 'Flat'
  return pnl > 0 ? 'Win' : 'Loss'
}

export default function TradesTable({ trades }) {
  if (!trades || trades.length === 0) {
    return <div className="trades-empty">No trades.</div>
  }

  return (
    <div className="trades-table-wrap">
      <table className="data-table trades-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Direction</th>
            <th>Entry Time</th>
            <th className="align-right">Entry Price</th>
            <th>Exit Time</th>
            <th className="align-right">Exit Price</th>
            <th className="align-right">P&amp;L</th>
            <th className="align-right">Return %</th>
            <th>Result</th>
            <th>Exit Reason</th>
          </tr>
        </thead>
        <tbody>
          {trades.map((t, i) => {
            const pct = pnlPct(t)
            const result = resultLabel(t.pnl)
            return (
              <tr key={i}>
                <td>{i + 1}</td>
                <td className={`trade-direction trade-${t.direction}`}>{t.direction}</td>
                <td>{formatDateTime(t.entry_time)}</td>
                <td className="align-right"><MetricValue value={t.entry_price} format="currency" /></td>
                <td>{formatDateTime(t.exit_time)}</td>
                <td className="align-right"><MetricValue value={t.exit_price} format="currency" /></td>
                <td className="align-right"><MetricValue value={t.pnl} format="currency" /></td>
                <td className={`align-right trade-return trade-return-${result.toLowerCase()}`}>
                  {pct === null ? '—' : `${pct >= 0 ? '+' : ''}${pct.toFixed(2)}%`}
                </td>
                <td>
                  <span className={`trade-result-badge trade-result-${result.toLowerCase()}`}>{result}</span>
                </td>
                <td className={`exit-reason exit-${t.exit_reason}`}>{t.exit_reason || '—'}</td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
